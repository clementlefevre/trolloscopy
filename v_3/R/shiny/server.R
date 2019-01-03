library(shinydashboard)
library(RColorBrewer)
library(dplyr)


library(RSQLite)

library(plotly)
library(lubridate)

Sys.setlocale("LC_ALL", "English")

DB.NAME <- '../../data/db/livefyre.db'




connect_to_db <- function() {
  tryCatch({
    con <- dbConnect(RSQLite::SQLite(), DB.NAME)
    return(con)
  },
  error = function(cond) {
    message(paste("could open DB connection", DB.NAME))
    return(NULL)
  })
}

read_df_from_db <- function(table.name) {
  con <- connect_to_db()
  
  tryCatch({
    df <- (dbReadTable(con, table.name))
    dbDisconnect(con)
    
    
    return (df)
  },
  error = function(cond) {
    message(paste("Database Table : ", table.name , " does not seem to exist:"))
    
    return(NULL)
  })
  dbDisconnect(con)
  
  
}


df.authors <- read_df_from_db('authors')
df.titles <- read_df_from_db('titles')
df.comments <- read_df_from_db('comments')
df.comments$createdAt <-
  as.POSIXct(df.comments$createdAt,  origin = "1970-01-01", tz = 'CET')
df.comments$hms <-
  strftime(df.comments$createdAt, format = "%H:%M:%S")
df.comments$weekday <- as.POSIXlt(df.comments$createdAt)$wday
df.comments$day <- wday(df.comments$createdAt, label = TRUE)
df.comments$monthday <-  as.POSIXlt(df.comments$createdAt)$mday
df.comments$year <- year(df.comments$createdAt)
df.comments$month <- month(df.comments$createdAt)

df.text <- read_df_from_db('text')

# df.likes <- read_df_from_db('likes')
# df.likes <- merge(df.likes,df.comments %>% select(authorId,id), by.x='comment_id', by.y='id')
# df.groupy <- df.likes %>% group_by(authorId,likedBy) %>% summarise(likes_count = n())
# df.groupy <- merge(df.groupy,df.authors,by.x='authorId',by.y='author_id')

df.groupy <- read.csv('df_likes.csv')

df.top.authors <-
  df.comments %>% group_by(authorId) %>% summarise(total_comments = n())   #%>% top_n(1000)
df.top.authors <-
  merge(
    df.top.authors,
    df.authors,
    by.x = 'authorId',
    by.y = 'author_id',
    all.x = TRUE
  )  %>% dplyr::arrange(desc(total_comments)) %>% na.omit()



filter_comment <- function(df,
                           authorId.filter,
                           year.filter,
                           month.filter) {
  df <-
    df %>% filter((month == month.filter) & (year == year.filter))
  df <- merge(df, df.titles, by = 'ft_id', all.x = TRUE)
  year(df$createdAt) <- 2019
  month(df$createdAt) <- 1
  day(df$createdAt) <- 1
  
  
  df <- merge(df, df.authors, by.x = 'authorId', by.y = 'author_id')
  
  return (df)
  
}

create_interactions_table <- function(authorId.selected) {
  df.test <-
    df.comments %>% transform(ancestorId = ifelse(ancestorId == -1, id, ancestorId))
  
  df.comments.written <-
    df.test %>% filter(authorId == authorId.selected) %>% select(ancestorId)
  
  df.comment.involved <-
    merge(df.test, df.comments.written, by = 'ancestorId') %>% filter(authorId !=
                                                                        authorId.selected)
  
  df.groupy <-
    df.comment.involved %>% group_by(authorId) %>% summarise(total_interactions = n())
  
  df.groupy <- df.groupy %>% top_n(20)
  df.groupy <-
    merge(df.groupy, df.authors, by.x = 'authorId', by.y = 'author_id') %>%
    arrange(desc(total_interactions))
  df.groupy <- df.groupy %>% select(displayName, total_interactions)
  
  return (df.groupy)
  
}



likes.ranking <- function(authorId.filter) {
  df <-
    df.groupy %>% filter(authorId  %in% authorId.filter) %>% arrange(desc(likes_count))
  df <-
    merge(
      df,
      df.authors,
      by.x = 'likedBy',
      by.y = 'author_id',
      suffixes = c('author', 'liker')
    )
  df <- df %>% select(displayNameliker, likes_count)
  df <- df %>% dplyr::arrange(desc(likes_count)) %>% top_n(20)
  return (df)
}



function(input, output, session) {
  filter.on.authors <-  reactive({
    df <-
      df.comments %>% dplyr::filter(authorId %in% input$author.select)
    
    df <- df %>% transform(id.color = as.integer(factor(authorId)))
    
    df$date <- as.Date(df$createdAt)
    
    palette <- brewer.pal(length(input$author.select), "Dark2")
    df <- df %>% transform(color.id = palette[id.color])
    
    df
    
  })
  
  authors.lists <-
    structure(as.character(df.top.authors$authorId),
              names = as.character(df.top.authors$displayName))
  
  
  
  output$author.select <- renderUI({
    selectizeInput(
      inputId = "author.select",
      label = "Authors",
      choices = authors.lists,
      selected = '56645@ft.fyre.co',
      multiple = TRUE
    )
  })
  
  output$author.tab2.select <- renderUI({
    selectizeInput(
      inputId = "author.tab2.select",
      label = "Authors",
      choices = authors.lists,
      selected = '56645@ft.fyre.co',
      multiple = FALSE
    )
  })
  
  output$year.select <- renderUI({
    selectInput(inputId = "year.select",
                label = "Year",
                choices = sort(unique(df.comments$year)))
  })
  
  output$month.select <- renderUI({
    selectInput(inputId = "month.select",
                label = "Month",
                choices = sort(unique(df.comments$month)))
  })
  
  
  output$likes.table <- renderTable({
    df <-   likes.ranking(input$author.tab2.select)
    df
  })
  
  output$interactions.table <-renderTable({
    
    df <- create_interactions_table(input$author.tab2.select)
    df
  })
  
  
  
  output$timeline.monthly <- renderPlotly({
    # add validate here
    validate(
      need(input$author.select != "", "No school selected"),
      need(input$year.select != "", "No school selected")# display custom message in need
    )
    
    df <- filter.on.authors()
    df <- filter_comment(df,
                         input$author.select,
                         input$year.select,
                         input$month.select)
    
    
    
    df <-
      merge(df,
            df.text %>% select(-index),
            by = 'id',
            all.x = TRUE)
    
    
    
    
    
    a <- list(
      autotick = FALSE,
      ticks = "outside",
      tick0 = 0,
      dtick = 1,
      ticklen = 1,
      tickwidth = 1,
      tickcolor = toRGB("blue"),
      range = c(0, 32)
      
    )
    
    #df$text <- paste(strwrap(df$bodyHtml,150), collapse='<br>')
    
    #browser()
    p <- plot_ly(source = "source")
    for (i in unique(df$color.id)) {
      p <- p  %>%
        add_markers(
          x = df$createdAt[df$color.id == i],
          y = df$monthday[df$color.id == i],
          name = df$displayName[df$color.id == i][1],
          marker = list(color = i, symbol = 'square'),
          text =  paste('<b>', df$title[df$color.id == i], hoverinfo = 'text')
          
        )
      
    }
    
    
    
    p  %>%
      layout(
        yaxis = a,
        xaxis = list(
          range =
            c(
              as.POSIXct("2019-01-01 00:00:00") ,
              as.POSIXct("2019-01-01 23:59:59")
            ),
          type = "date"
        ),
        showlegend = FALSE
      )
    
    
    
  })
  
  
  
  output$click <- renderPrint({
    eventdata <- event_data(source = "source")
    
    createdAt.hover <- eventdata$x
    day.hover <- as.numeric(eventdata$y)
    
    df <- filter.on.authors()
    df <- filter_comment(df,
                         input$author.select,
                         input$year.select,
                         input$month.select)
    
    df <-
      merge(df,
            df.text %>% select(-index),
            by = 'id',
            all.x = TRUE)
    
    
    df.text <-
      df %>% filter((monthday == day.hover)  &
                      (createdAt == createdAt.hover))
    df.text$bodyHtml
    
  })
  
  
  output$timeline.overall <- renderPlotly({
    # add validate here
    validate(need(input$author.select != "", "No Author selected"))
    
    
    df <- filter.on.authors()
    
    df <-
      df %>% group_by(date, authorId, color.id, id.color) %>% summarise(comments_count = n())
    
    df <-
      merge(df, df.authors, by.x = 'authorId', by.y = 'author_id')
    
    authorId.to.plot.list <- unique(df$color.id)
    
    
    plot_list <-
      lapply(authorId.to.plot.list, function(authorId.to.plot) {
        df.i <- df %>% filter(color.id == authorId.to.plot)
        print(authorId.to.plot)
        
        p <- plot_ly(
          data = df.i,
          x = ~ date,
          y = ~ comments_count,
          name = ~ displayName,
          type = 'bar',
          marker = list(color = df.i$color.id)
          
        ) %>%
          layout(xaxis = list(
            range =
              c(
                as.POSIXct("2014-01-01 00:00:00"),
                as.POSIXct("2019-01-01 23:59:59")
              ),
            type = "date"
          ))
        p
        
      })
    
    
    
    p <-
      subplot(plot_list,
              nrows = length(plot_list) ,
              shareX = TRUE)
    p
  })
  
}
