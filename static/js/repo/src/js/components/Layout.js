import React from "react"
import axios from "axios";
import { connect } from "react-redux"

import { fetchRepo } from "../actions/repoActions"
import { fetchFiles } from "../actions/filesActions"
//import { fetchTags } from "../actions/tagsActions"

import Branches from "./Branches"
import Dropzone from 'react-dropzone'
import request from 'superagent';

require('superagent-django-csrf');





@connect((store) => {
  return {
    repo: store.repo.repo,
    files: store.files,
  };
})
export default class Layout extends React.Component {
  constructor() {
      super()
      this.state = {
        accept: '',
        files: [],
        dropzoneActive: false
      }
    }

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



  onDrop(files) {
    this.setState({
      files: files,
      dropzoneActive: false
    });
    var file = new FormData();
    const Throttle = require('superagent-throttle')
    let throttle = new Throttle({
      active: true,     // set false to pause queue
      rate: 1,          // how many requests can be sent every `ratePer`
      ratePer: 1000,   // number of ms in which `rate` requests may be sent
      concurrent: 1     // how many requests can be sent concurrently
    })
    var req=request
              .post(`/api/v1/files/${window.props.repo_id}/${window.props.directory}/`)
              .use(throttle.plugin())
    files.forEach((dropped_file) => {



      req.attach('name', dropped_file);
      //file.append('name',dropped_file)

      });
      req.send
      req.end(function(err,response){
          console.log("upload done!!!!!");
    })






  }
  onDragEnter() {
    this.setState({
      dropzoneActive: true
    });
  }

  onDragLeave() {
    this.setState({
      dropzoneActive: false
    });
  }
  applyMimeTypes(event) {
    this.setState({
      accept: event.target.value
    });
  }


  render() {
    const { repo, files, is_author } = this.props;
    const { accept, dropzoneActive } = this.state;
    const overlayStyle = {
      position: 'absolute',
      top: 0,
      right: 0,
      bottom: 0,
      left: 0,
      padding: '2.5em 0',
      background: 'rgba(0,0,0,0.5)',
      textAlign: 'center',
      color: '#fff'
    };

    console.log('this.props.files', this.props.files)
    console.log('files', files)
    console.log('this.props.files.fetched',this.props.files.fetched)

    const editShow = (files.is_owner) ? <a href={`setting/`} style={{color: '#999', fontSize: '.75em'}}>edit</a> : null

    // function folderShow() {
    //   const directory = window.props.directory
    //   let dir_split = directory.split("/")
    //   let working_dir = ""
    //   let working_html = ""
    //   dir_split.forEach((folder) => {
    //     working_dir += folder + "/"
    //     working_html.push(<font>/ <a href={`/${window.props.owner_name}/${window.props.repo_name}/${working_dir}`}>{folder}</a></font>)
    //   })
    //   console.log('working_html', working_html)
    //   return working_html
    // }

    const dir_array = window.props.directory.split("/")


    function folders() {
      let working_dir = ""
      let last = dir_array.length - 1
      const arrayList = dir_array.map((folder, i) => {
        working_dir += folder
        let words = null
        if (i == last) {
            words = <font>/ {folder} </font>
        }
        else {
            words = <font>/ <a href={`/${window.props.repo_owner}/${window.props.repo_name}/${working_dir}`}>{folder}</a> </font>
        }
        working_dir += "/"
        return words
      })
      return arrayList
    }

    if (!this.props.files.fetched) {
            return <p>Loading…</p>;
    }
    if (!this.props.files.time) {
            return <p>Loading...</p>
    }




    return <div>
      <Dropzone
        disableClick
        style={{}}
        accept={accept}
        onDrop={this.onDrop.bind(this)}
        onDragEnter={this.onDragEnter.bind(this)}
        onDragLeave={this.onDragLeave.bind(this)}
      >
      <div className="row">
        <div className="col-md-6 col-xs-8">
          <p>
            <h2 className="repo-header"><a href={`/${window.props.repo_owner}`}>{window.props.repo_owner}</a> / <a href={`/${window.props.repo_owner}/${window.props.repo_name}`}>{window.props.repo_name}</a> </h2>
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

          <Branches branches={files.branches} is_owner={files.is_owner} />

          <p className="dir-tree"><a href={`/${window.props.repo_owner}/${window.props.repo_name}`}>{`${window.props.repo_name}`}</a> {folders()}</p>

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
                const editLink = (files.is_owner) ? (file.type == 'blob') ? <a href={`/${window.props.repo_owner}/${window.props.repo_name}/${(window.props.directory !== '') ? `${window.props.directory}/` : ``}blob/${file.name}/edit`} style={{fontSize: '.75em', color: '#999'}}>edit</a>: null : null
                const fileLink = (file.type == 'blob' && window.props.directory !== "") ? <a href={`/${window.props.repo_owner}/${window.props.repo_name}/${window.props.directory}/blob/${file.name}`}>{ file.name }</a> : (file.type == 'blob') ? <a href={`blob/${file.name}`}>{ file.name }</a> : <a href={`/${window.props.repo_owner}/${window.props.repo_name}/${(window.props.directory !== '') ? `${window.props.directory}/` : ``}${file.name}`}>{ file.name }</a>
                const deleteLink = (files.is_owner && file.type == 'blob') ? <a href={`/${window.props.repo_owner}/${window.props.repo_name}/${(window.props.directory !== '') ? `${window.props.directory}/` : ``}blob/${file.name}/delete`}><font style={{fontSize: '.75em', color: '#f33'}}>delete</font></a> : null
                return <tr key={file.id}><th scope="row">{icon} {fileLink} &nbsp;{editLink}</th><td>{deleteLink}</td><td><a href={`commit/${file.id}`}>{file.id}</a></td></tr>
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
          { files.is_owner &&
            <div>
          <section>
            <div className="dropzone">
              <Dropzone
                onDrop={this.onDrop.bind(this)}
                className="dropzone"
                >
                <p>&nbsp;&nbsp;<b>Upload Files:</b> To upload files, drag & drop files anywhere above. Or click this box to select files to upload.</p>
              </Dropzone>
            </div>
            <aside>
              { this.state.files[0] &&
                <div>
                  <h2>Dropped files</h2>
                  <ul>
                    {
                      this.state.files.map(f => <li key={f.name}>{f.name} - {f.size} bytes</li>)
                    }
                  </ul>
                </div>
              }
            </aside>
          </section>
        </div>
          }




        </div>
      </div>
      </Dropzone>
    </div>
  }
}
