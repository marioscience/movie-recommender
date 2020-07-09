import React from "react";
import {Link} from "react-router-dom";

import user from './static/user.svg';

import './navbar.css';

class Navbar extends React.Component {
    render() {
        return (<div id="navbar">
                    <div className="header"><Link to={`/`}><h1 className="header-title">Movie Recommender</h1></Link></div>
                    <div className="links"><ul></ul></div>
                    <div className="user-box"><img src={user} className="navbar-icon" alt="logo" /> <h3>Welcome, John Doe.</h3></div>
                </div>);
    }
}

export default Navbar;
