from apscheduler.jobstores.mongodb import MongoDBJobStore

job_stores = {
    'default': MongoDBJobStore(host=f'mongodb+srv://lauralex:coccode@apldb.hhz9g.mongodb.net/db_apl?retryWrites=true&w=majority')
}