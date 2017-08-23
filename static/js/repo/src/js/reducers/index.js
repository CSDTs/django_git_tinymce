import { combineReducers } from "redux"

import repo from "./RepoReducer"
import files from "./filesReducer"

export default combineReducers({
  repo,
  files
})
