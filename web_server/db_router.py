class DistributedRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in ['user', 'settings']:
            return db == 'parser'
        if model_name in ['search', 'betdata']:
            return db == 'betdata'
        return True