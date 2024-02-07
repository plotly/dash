/*
 * dash renderer is purposely style-free
 * Dash apps should be styled through
 * CSS style sheets on the app level,
 * in component-suites, or as inline styles
 * in the component layouts.
 *
 * The styles contained in dash-renderer are
 * just for a couple of interfaces:
 * - Loading messages
 * - Login screens
 *
 */

export const base = {
    html: {
        fontFamily: "'Open Sans', Helvetica, sans-serif",
        fontWeight: 400,
        color: '#2A3F5F'
    },

    h2: {
        fontFamily: 'Dosis, Helvetica, sans-serif',
        fontWeight: '600',
        fontSize: '28px',
        marginTop: '14px',
        marginBottom: '14px'
    },

    h4: {
        fontSize: '18px',
        marginTop: '9px',
        marginBottom: '18px'
    },

    button: {
        border: '1px solid #119DFF',
        fontSize: '14px',
        color: '#ffffff',
        backgroundColor: '#119DFF',
        padding: '9px 18px',
        borderRadius: '5px',
        textAlign: 'center',
        textTransform: 'capitalize',
        letterSpacing: '0.5px',
        lineHeight: '1',
        cursor: 'pointer',
        outline: 'none',
        margin: '0px'
    },

    a: {
        color: '#119DFF',
        textDecoration: 'none',
        cursor: 'pointer'
    },

    caption: {
        fontSize: '13px',
        marginTop: '20px',
        color: '#A2B1C6'
    },

    container: {
        marginLeft: 'auto',
        marginRight: 'auto',
        width: '90%',
        maxWidth: '300px'
    }
};

export default base;
