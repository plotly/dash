import {expect} from 'chai';
import {describe, it} from 'mocha';
import {errorToText} from '../src/components/error/FrontEnd/errorText';

describe('errorToText', () => {
    it('joins the message and the frontend stack trace', () => {
        const text = errorToText({
            message: 'Something broke',
            stack: 'Error: Something broke\n    at foo (bar.js:1:1)'
        });
        expect(text).to.equal(
            'Something broke\n\nError: Something broke\n    at foo (bar.js:1:1)'
        );
    });

    it('prefers the plain traceback of a werkzeug debugger page', () => {
        const html =
            '<!doctype html><html><body><div class="debugger">' +
            '<h1>ZeroDivisionError</h1><div class="plain">' +
            '<textarea cols="50" rows="10" name="code" readonly>' +
            'Traceback (most recent call last):\n  File "app.py", line 3\n' +
            'ZeroDivisionError: division by zero\n</textarea></div></div>' +
            '</body></html>';
        const text = errorToText({message: 'Callback error', html});
        expect(text).to.equal(
            'Callback error\n\nTraceback (most recent call last):\n' +
                '  File "app.py", line 3\nZeroDivisionError: division by zero'
        );
    });

    it('falls back to the text content of an html fragment', () => {
        const text = errorToText({html: '<div><b>Oops</b> bad value</div>'});
        expect(text).to.equal('Oops bad value');
    });

    it('returns plain text errors unchanged', () => {
        expect(errorToText({html: 'Internal Server Error'})).to.equal(
            'Internal Server Error'
        );
    });

    it('returns an empty string when there is nothing to copy', () => {
        expect(errorToText({})).to.equal('');
    });
});
