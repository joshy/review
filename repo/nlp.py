from mlzoo.risnlp_groups.gastro_internal.fs18_svc import model


def classify(text):
   return model.predict(text, None)