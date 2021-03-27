
##### NEWS API
{
    "endpoint":"headlines",
    "query" : {
      "category": "general",
      "language": "en"
    }

}


##### REDDIT 
{
    "endpoint":"not logged in",
    "query" : {
      "subreddit_name":"news",
    "sort_order":"top",
    "items_limit":6
    }

}


#### BING 
## Search - 
{
  "endpoint":"search",
  "query" : {
    "q":"",
    "mkt":"en-US",
    "sortBy":"Date",
    "count":100
  }

}

{
  "endpoint":"search",
  "query" : {
    "q":"coronavirus",
    "mkt":"en-US",
    "sortBy":"Date",
    "freshness": "Day",
    "count":100
  }

}

## Category
{
  "endpoint":"category",
  "query" : {
    "category":"Business",
    "mkt":"en-US",
    "sortBy":"Date",
    "count":100
  }

}





