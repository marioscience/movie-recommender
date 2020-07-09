import React from "react";
import "./App.css";

import { Route, Switch } from 'react-router-dom';

import Navbar from "./components/navbar/navbar";
import Footer from "./components/footer/footer";
import Movie from "./components/movie/movie";
import Trending from "./components/trending/trending";

import Error from './components/404/404';

function App() {
  return (
    <div className="App">
      <Navbar></Navbar>
      <Switch>
          <Route path="/" component={Trending} exact />
          <Route path="/movie/:movieId" component={Movie} />
          <Route component={Error} />
      </Switch>
      <Footer></Footer>
    </div>
  );
}

export default App;
