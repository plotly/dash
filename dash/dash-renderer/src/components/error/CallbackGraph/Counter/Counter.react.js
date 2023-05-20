/* 
import './App.css';

import { Portal, PortalWithState } from 'react-portal';
import { useEffect, useState, Fragment } from 'react';
import { NewWindow } from './NewWindow';
 */

import {useEffect} from 'react';

export function Counter(props) {
    useEffect(() => {
        //console.log('$$$$$$$$$$ Counter init')
    }, []);

    return <>App test {props.counter}</>;
}
