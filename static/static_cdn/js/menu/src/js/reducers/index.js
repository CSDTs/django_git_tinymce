import { combineReducers } from "redux"
import { routerReducer } from 'react-router-redux';

import repos from "./ReposReducer"
import tags from "./tagsReducer"

export default combineReducers({
  repos,
  tags,
  routing: routerReducer,
})
