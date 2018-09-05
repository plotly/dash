import { ITarget } from 'dash-table/virtualization/AbstractStrategy';

import BackEndVirtualization from 'dash-table/virtualization/BackEndVirtualization';
import FrontEndVirtualization from 'dash-table/virtualization/FrontEndVirtualization';
import NoVirtualization from 'dash-table/virtualization/NoVirtualization';

export default class VirtualizationFactory {
    public static getVirtualizer(target: ITarget) {
        switch (target.virtualization) {
            case false:
                return new NoVirtualization(target);
            case true:
            case 'fe':
                return new FrontEndVirtualization(target);
            case 'be':
                return new BackEndVirtualization(target);
            default:
                throw new Error(`Unknown virtualization type: '${target.virtualization}'`);
        }
    }
}