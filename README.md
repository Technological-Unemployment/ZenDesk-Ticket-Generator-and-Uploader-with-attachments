#  Ticket Generator and Uploader with attachments
 Using SQL generate charts and create tickets and upload charts in ZenDesk by customer name.
 
Before you start go into ZenDesk to generate your token and make sure your domain is correct and your email associated with ZenDesk has read/write access.

The script assumes you're using a Postgresql schema. You can easily change the def QsearchT(name) and def QsearchD(name) to the SQL version that suits your needs.

The ZenDesk API was used to generate and upload the ZenDesk tickets.
