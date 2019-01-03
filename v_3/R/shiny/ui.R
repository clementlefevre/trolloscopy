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
    
    fluidRow(column(
      width = 10,
      box(
        width = NULL,
        solidHeader = TRUE,
        
        plotlyOutput("timeline.overall")
      )
    ),
    column(width = 2))
  ),
  
  tabItem(
    tabName = "widgets",
    uiOutput("author.tab2.select"),
    fluidRow(column(width = 6, box(
      tableOutput('likes.table')
    )), column(width = 6,
               box(
                 tableOutput('interactions.table')
               )))
    
  )
))

dashboardPage(header,
              sidebar,
              body)