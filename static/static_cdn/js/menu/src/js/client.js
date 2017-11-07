import React from "react"
import ReactDOM from "react-dom"
import { Provider } from "react-redux"
import {
  BrowserRouter as Router,
  Route,
  browserHistory
} from 'react-router-dom';
import history from './history';



import Layout from "./components/Layout"
import store from "./store"

const app = document.getElementById('app')


ReactDOM.render(<Provider store={store}>
  <Router>
    <Route path='/' component={Layout}/>
  </Router>
</Provider>, app);
