library(RSQLite)

DB.NAME <- '../../data/db/livefyre.db'



connect_to_db <- function(){
  tryCatch(
    {
      con <- dbConnect(RSQLite::SQLite(), DB.NAME)
      return(con)
    },
    error=function(cond) {
      message(paste("could open DB connection", DB.NAME))
      return(NULL)
    }
  )
}

read_df_from_db <- function(table.name){
  con <- connect_to_db()
  
  tryCatch(
    {
      df <- (dbReadTable(con,table.name))
      dbDisconnect(con)

      
      return (df)
    },
    error=function(cond) {
      message(paste("Database Table : ", table.name , " does not seem to exist."))
      
      return(NULL)
    }
  ) 
  dbDisconnect(con)
  
}

query_df_from_db <- function(query_string){
  con <- connect_to_db()
  
  tryCatch(
    {
      df <- (dbGetQuery(con,query_string))
      dbDisconnect(con)
      
      
      return (df)
    },
    error=function(cond) {
      message(paste("Database Table : ", table.name , " does not seem to exist."))
      
      return(NULL)
    }
  ) 
  dbDisconnect(con)
  
}



insert_df_to_db <- function(df, table.name){
  con <- dbConnect(RSQLite::SQLite(), DB.NAME)
  dbWriteTable(con, table.name, df,overwrite = TRUE)
  dbDisconnect(con)
}
