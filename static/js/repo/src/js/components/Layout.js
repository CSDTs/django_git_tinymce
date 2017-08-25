import React from "react"
import axios from "axios";
import { connect } from "react-redux"

import { fetchRepo } from "../actions/repoActions"
import { fetchFiles } from "../actions/filesActions"
//import { fetchTags } from "../actions/tagsActions"

import Branches from "./Branches"


@connect((store) => {
  return {
    repo: store.repo.repo,
    files: store.files,
  };
})
export default class Layout extends React.Component {
  componentDidMount() {
    //this.props.dispatch(fetchUser())
    this.props.dispatch(fetchRepo())
    //this.props.dispatch(fetchTags())
    this.props.dispatch(fetchFiles())
  }

  getIcon(type) {
    switch(type) {
      case 'blob':
        return <i class="glyphicon glyphicon-list-alt"/>
      case 'tree':
        return <i class="glyphicon glyphicon-folder-close"/>
    }
  }

  timeFormat(timeStr) {
    timeStr = timeStr.substring(1)
    timeStr = timeStr.substring(0, timeStr.length - 1)
    timeStr = timeStr.replace(/T/g , " ");
    return timeStr
  }


  render() {
    const { repo, files, is_author } = this.props;

    console.log('this.props.files', this.props.files)
    console.log('files', files)
    console.log('this.props.files.fetched',this.props.files.fetched)

    const editShow = (files.is_owner) ? <a href={`setting/`} style={{color: '#999', fontSize: '.75em'}}>edit</a> : null


    if (!this.props.files.fetched) {
            return <p>Loading…</p>;
    }
    if (!this.props.files.time) {
            return <p>Loading...</p>
            // <div className="row">
            //   <div className="col-md-12">
            //     <p>
            //       <h2 className="repo-header"><a href={`/${window.props.repo_owner}`}>{window.props.repo_owner}</a> / <a href={`/${window.props.repo_owner}/${window.props.repo_name}`}>{window.props.repo_name}</a></h2>
            //     </p>
            //
            //     <p>
            //       <h4 className="repo-header">{repo.description} {editShow}</h4>
            //     </p>
            //     <p><Branches branches={files.branches}/></p>
            //   </div>
            // </div>
    }




    return <div>
      <div className="row">
        <div className="col-md-6 col-xs-8">
          <p>
            <h2 className="repo-header"><a href={`/${window.props.repo_owner}`}>{window.props.repo_owner}</a> / <a href={`/${window.props.repo_owner}/${window.props.repo_name}`}>{window.props.repo_name}</a></h2>
          </p>
        </div>
        <div className="col-md-6 text-right col-xs-4">
          {files.is_owner &&
          <div class="btn-group ">
            <button type="button" class="btn btn-danger"><i className="glyphicon glyphicon-cog"/></button>
            <button type="button" class="btn btn-danger dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <span class="caret"></span>
              <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
              <li><a href={`setting/`}>Edit Description</a></li>
              <li role="separator" class="divider"></li>
              <li><a href={`/${window.props.repo_owner}/${window.props.repo_name}/delete`}><font style={{color: '#f33'}}>Delete Repo</font></a></li>
            </ul>
          </div>
        }
        </div>
      </div>
      <div className="row">
        <div className="col-md-12">
          <p>
            <h4 className="repo-header">{repo.description} {editShow}</h4>

          </p>

          <Branches branches={files.branches} is_owner={files.is_owner}/>

          <div class="panel panel-success">
            {(files.committer) ? <div class="panel-heading">Last commit message by <a href={`/${files.committer}`}>{files.committer}</a>: <a href={`commit/${files.hex}`}>{files.message} <font style={{color: '#999'}}><i>({this.timeFormat(files.time)})</i></font></a></div> : <div class="panel-heading">No Files Yet</div> }
            <table class="table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th></th>
                  <th>Last Commit</th>
                </tr>
              </thead>
              <tbody>

              {this.props.files.files.map((file) => {
                const icon = this.getIcon(file.type)
                const editLink = (files.is_owner) ? <a href={`blob/${file.name}/edit`} style={{fontSize: '.75em', color: '#999'}}>edit</a> : null
                return <tr key={file.id}><th scope="row">{icon} <a href={`blob/${file.name}`}>{ file.name }</a> &nbsp;{editLink}</th><td>{ files.is_owner && <a href={`blob/${file.name}/delete`}><font style={{fontSize: '.75em', color: '#f33'}}>delete</font></a>}</td><td><a href={`commit/${file.id}`}>{file.id}</a></td></tr>
              })}
              </tbody>
            </table>
          </div>
          <p>

          </p>
        </div>
      </div>
      <div className="row">
        <div className="col-md-12">




        </div>
      </div>

    </div>
  }
}
