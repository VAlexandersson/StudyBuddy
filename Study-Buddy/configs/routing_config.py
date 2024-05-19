ROUTING_CONFIG = {
  "ClassifyQueryTask": {
    "rag": "EmbedQueryTask",
    "general": "GenerateResponseTask"
  },
  "DecomposeQueryTask": {
    None: "RetrieveDocumentsTask"
  },
  "EmbedQueryTask": {
    None: "RetrieveDocumentsTask"
  },
  "GenerateResponseTask": {
    None: "GradeResponseTask"
  },
  "GradeResponseTask": {
    None: "EndTask"
  },
  "PreprocessQueryTask": {
    None: "ClassifyQueryTask"
  },
  "ReRankingTask": {
    None: "FilterDocumentsTask"
  },
  "RetrieveDocumentsTask": {
    None: "ReRankingTask"
  },
  "FilterDocumentsTask": {
    None: "GenerateResponseTask"
  }
}