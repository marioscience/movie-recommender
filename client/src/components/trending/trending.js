import React from 'react';
import MovieList from "../movielist/movielist";
class Trending extends React.Component {
    constructor(props) {
        super(props);
        this.state = {movies: []};
    }

    componentDidMount() {
        const url = "http://localhost:5000/api/trending";
        fetch(url)
            .then(response => response.json())
            .then(movies => this.setState({movies: movies}))
            .catch(e => console.log(e.message))
    }

    render() {
        return (
            <div>
                <h2>Top Trending Movies...</h2>
                <MovieList movies={this.state.movies}></MovieList>
            </div>
        )
    }
}

export default Trending;