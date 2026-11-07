from app.services.data import MyDataFrame

def get_dataset_info():
    return {'rows':len(MyDataFrame().getMyDataFrame()),'columns':list(MyDataFrame().getMyDataFrame().columns)}

