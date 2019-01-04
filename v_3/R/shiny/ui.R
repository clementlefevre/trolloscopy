library(shinydashboard)

library(plotly)

header <- dashboardHeader(title = "Trolloscopy")

sidebar <- dashboardSidebar(sidebarMenu(
  menuItem(
    "Dashboard",
    tabName = "dashboard",
    icon = icon("dashboard")
  ),
  menuItem(
    "Widgets",
    icon = icon("th"),
    tabName = "widgets",
    badgeLabel = "new",
    badgeColor = "green"
  )
))



body <- dashboardBody(tabItems(
  tabItem(
    tabName = "dashboard",
    fluidRow(column(
      width = 9,
      box(
        width = NULL,
        solidHeader = TRUE,
        plotlyOutput("timeline.monthly"),
        verbatimTextOutput("click")
      )
    ),
    column(
      width = 3,
      box(
        uiOutput("author.select"),
        uiOutput("year.select"),
        uiOutput("month.select")
      )
    )),
    
    fluidRow(
      box(
        width = NULL,
        solidHeader = TRUE,
        
        plotlyOutput("timeline.overall")
      )
    )
  ),
  
  tabItem(
    tabName = "widgets",
    uiOutput("author.tab2.select"),
    uiOutput("year.select.pca"),
    fluidRow(box(width = NULL,
                 solidHeader = TRUE,plotlyOutput("pca"))),
    
    fluidRow(column(width = 4, box(
      tableOutput('likes.table')
    )), column(width = 4,
               box(
                 tableOutput('interactions.table')
               )),
    column(width=4,box(tableOutput("tfidf.table")))
    )
    
  )
))

dashboardPage(header,
              sidebar,
              body)