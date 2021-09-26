# GIFT-REST API
Api written using flask and requests which scrapes content on cms.gift.edu.in

Hosted on [Heroku](https://gift-rest-flask.herokuapp.com/)

## Endpoints
**[POST]** `/student/data`
with the body
```
{
"id":"12345678",
"pass":"12345678"
}
```
## Data Returned

 - Basic- Name,Branch etc
 - Personal
 - Academic
 - Fees Details
 - Guardian Details
 - Addresses
 - Attendance
 - Id card details with link
