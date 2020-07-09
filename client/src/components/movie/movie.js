import React from 'react';
import MovieList from '../movielist/movielist';
import './movie.css';

class Movie extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            similarMovies: [],
            movie: {},
            isFlushed: false
        }
    }

    fetchData() {
        const currentUser = 5; // Mocking user for now, should come from user service
        const movieId = this.props.match.params.movieId;
        const similarUrl = `http://localhost:5000/api/similar/${movieId}`;
        const rateUrl = `http://localhost:5000/api/rate/${currentUser}/${movieId}`;

        fetch(similarUrl)
            .then(response => response.json())
            .then(movies => this.setState({similarMovies: movies}))
            .catch(e => console.log(e.message));

        fetch(rateUrl)
            .then(response => response.json())
            .then(movie => this.setState({movie: movie[0]}))
            .catch(e => console.log(e.message));
    }

    componentDidMount() {
        this.fetchData()
    }

    componentWillReceiveProps(nextProps, nextContext) {
        if (!this.props.flush && nextProps.flush) {
            this.setState({isFlused: false})
        }

        if (!this.state.isFlushed && nextProps.location.state === 'flush') {
            this.setState({
                isFlused: true
            },
            () => this.fetchData()
            )
        }
    }

    render() {
        let movieInfo;
        if (this.state.movie && Object.keys(this.state.movie).length > 0) {
            const runtimeHr = Math.floor(this.state.movie.runtime);
            const runtimeMn = (this.state.movie.runtime - runtimeHr) * 60;
            movieInfo = (
                <div className="movie-detail">
                    <div className="trailer-video" >
                        <div className="embed-div">
                        <embed
                            src={this.state.movie.trailer_url}
                            wmode="transparent"
                            type="video/mp4"
                            allow="autoplay; encrypted-media; picture-in-picture"
                            allowfullscreen
                            title="Keyboard Cat" />
                            </div>
                    </div>
                    <div className="movie-info">
                        <img src={this.state.movie.poster_url} alt=""/>
                        <h2>{this.state.movie.title}</h2>
                        <div>
                            <span>{this.state.movie.tagline}</span><br/>
                            <span><strong>Release Date: </strong>{new Date(this.state.movie.release_date).toLocaleDateString()}</span><br/>
                            <span><strong>Runtime: </strong>{runtimeHr + ":" + ("0" + runtimeMn).slice(-2)}</span><br/>
                            <h3><strong>We Believe You'll Rate it: </strong>{this.state.movie.predicted_rating.toFixed(2)}</h3>
                            <a className="watch-button" target="_blank" rel="noopener noreferrer" href={`https://www.netflix.com/search?q=${this.state.movie.title}`}>Watch now</a>
                            <a className="watch-button" target="_blank" rel="noopener noreferrer" href={this.state.movie.trailer_url}>Watch Trailer</a>
                        </div>
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

