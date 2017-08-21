import { combineReducers } from "redux"

import repos from "./ReposReducer"
import user from "./userReducer"
import tags from "./tagsReducer"

export default combineReducers({
  repos,
  user,
  tags,
})
