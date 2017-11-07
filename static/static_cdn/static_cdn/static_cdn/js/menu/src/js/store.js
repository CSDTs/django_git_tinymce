import { applyMiddleware, createStore } from "redux"

import logger from "redux-logger"
import thunk from "redux-thunk"
import promise from "redux-promise-middleware"

import reducer from "./reducers"
import { routerMiddleware, push } from 'react-router-redux'
import {browserHistory,withRouter} from 'react-router-dom';
import history from './history';




const middlewareHistory = routerMiddleware(history)

const middleware = applyMiddleware(promise(), thunk, logger(), middlewareHistory)

export default createStore(reducer, middleware)
