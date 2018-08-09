const initialError = {
  error: false,
  errorPage: ""
};

function error (state = initialError, action) {
    switch (action.type) {

        case 'ON_ERROR': {
            return {
                error: true,
                errorPage: action.payload
            };
        }

        case 'RESOLVE_ERROR': {
          return initialError;
        }

        default: {
            return state;
        }

    }
}

export default error;