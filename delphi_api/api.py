import storageClient
import apiHelper
import pprint

store = storageClient.StorageClient(None)
tools = apiHelper.ApiHelper(store)


stats = tools.get_stats()
pprint.pprint(stats)
