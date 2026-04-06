Need to add finally and try catch to some apis

Different files so its easy to find stuff

All APIs follow the same pattern:
Receive request data (JSON)
Validate required fields
Check authentication (logged in)
Check authorization (role if needed)
Run SQL query
Return JSON response

Test them with Example:
POST /api/login
POST /api/courses
GET /api/reports/top-students
