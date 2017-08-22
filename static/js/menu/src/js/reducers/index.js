import { combineReducers } from "redux"

import repos from "./ReposReducer"
import tags from "./tagsReducer"

export default combineReducers({
  repos,
  tags,
})
