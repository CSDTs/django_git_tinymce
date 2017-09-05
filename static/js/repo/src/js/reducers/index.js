import { combineReducers } from "redux"

import repo from "./RepoReducer"
import files from "./filesReducer"
import readme from "./readmeReducer"

export default combineReducers({
  repo,
  files,
  readme
})
