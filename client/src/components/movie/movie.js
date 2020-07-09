import React from 'react';
import MovieList from '../movielist/movielist';

class Movie extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            similarMovies: [],
            movie: {}
        }
    }

    componentDidMount() {
        const currentUser = 10; // Mocking user for now, should come from user service
        const movieId = this.props.match.params.movieId;
        const similarUrl = `http://localhost:5000/api/similar/${movieId}`;
        const rateUrl = `http://localhost:5000/api/rate/${currentUser}/${movieId}`

        fetch(similarUrl)
            .then(response => response.json())
            .then(movies => this.setState({similarMovies: movies}))
            .catch(e => console.log(e.message));

        fetch(rateUrl)
            .then(response => response.json())
            .then(movie => this.setState({movie: movie[0]}))
            .catch(e => console.log(e.message));
    }

    render() {
        let movieInfo;
        if (this.state.movie) {
            movieInfo = (
                <div>
                    <img src={this.state.movie.poster_url} alt=""/>
                    <h2>{this.state.movie.title}</h2>
                    <div>
                        <span>{this.state.movie.tagline}</span><br/>
                        <span>{this.state.movie.release_date}</span><br/>
                        <span>{this.state.movie.runtime}</span><br/>
                        <span>{this.state.movie.imdb_rating}</span>
                    </div>
                </div>
            )
        }
        return (
            <div>
                <div className="main-movie">
                    {movieInfo}
                </div>
                <div>
                    <h3>Similar Movies... </h3>
                    <MovieList movies={this.state.similarMovies}></MovieList>
                </div>
            </div>
        );
    }
}

export default Movie;

