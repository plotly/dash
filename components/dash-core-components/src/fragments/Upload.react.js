import React, {Component} from 'react';
import Dropzone from 'react-dropzone';

import {propTypes} from '../components/Upload.react';
import LoadingElement from '../utils/LoadingElement';

export default class Upload extends Component {
    constructor() {
        super();
        this.onDrop = this.onDrop.bind(this);
        this.getDataTransferItems = this.getDataTransferItems.bind(this);
    }

    // Check if file matches the accept criteria
    fileMatchesAccept(file, accept) {
        if (!accept) {
            return true;
        }

        const acceptList = Array.isArray(accept) ? accept : accept.split(',');
        const fileName = file.name.toLowerCase();
        const fileType = file.type.toLowerCase();

        return acceptList.some(acceptItem => {
            const item = acceptItem.trim().toLowerCase();

            // Exact MIME type match
            if (item === fileType) {
                return true;
            }

            // Wildcard MIME type (e.g., image/*)
            if (item.endsWith('/*')) {
                const wildcardSuffixLength = 2;
                const baseType = item.slice(0, -wildcardSuffixLength);
                return fileType.startsWith(baseType + '/');
            }

            // File extension match (e.g., .jpg)
            if (item.startsWith('.')) {
                return fileName.endsWith(item);
            }

            return false;
        });
    }

    // Recursively traverse folder structure and extract all files
    async traverseFileTree(item, path = '') {
        const {accept} = this.props;
        const files = [];

        if (item.isFile) {
            return new Promise(resolve => {
                item.file(file => {
                    // Check if file matches accept criteria
                    if (!this.fileMatchesAccept(file, accept)) {
                        resolve([]);
                        return;
                    }

                    // Preserve folder structure in file name
                    const relativePath = path + file.name;
                    Object.defineProperty(file, 'name', {
                        writable: true,
                        value: relativePath,
                    });
                    resolve([file]);
                });
            });
        } else if (item.isDirectory) {
            const dirReader = item.createReader();
            return new Promise(resolve => {
                const readEntries = () => {
                    dirReader.readEntries(async entries => {
                        if (entries.length === 0) {
                            resolve(files);
                        } else {
                            for (const entry of entries) {
                                const entryFiles = await this.traverseFileTree(
                                    entry,
                                    path + item.name + '/'
                                );
                                files.push(...entryFiles);
                            }
                            // Continue reading (directories may have more than 100 entries)
                            readEntries();
                        }
                    });
                };
                readEntries();
            });
        }
        return files;
    }

    // Custom data transfer handler that supports folders
    async getDataTransferItems(event) {
        const {multiple} = this.props;

        // If multiple is not enabled, use default behavior (files only)
        if (!multiple) {
            if (event.dataTransfer) {
                return Array.from(event.dataTransfer.files);
            } else if (event.target && event.target.files) {
                return Array.from(event.target.files);
            }
            return [];
        }

        // Handle drag-and-drop with folder support when multiple=true
        if (event.dataTransfer && event.dataTransfer.items) {
            const items = Array.from(event.dataTransfer.items);
            const files = [];

            for (const item of items) {
                if (item.kind === 'file') {
                    const entry = item.webkitGetAsEntry
                        ? item.webkitGetAsEntry()
                        : null;
                    if (entry) {
                        const entryFiles = await this.traverseFileTree(entry);
                        files.push(...entryFiles);
                    } else {
                        // Fallback for browsers without webkitGetAsEntry
                        const file = item.getAsFile();
                        if (file) {
                            files.push(file);
                        }
                    }
                }
            }
            return files;
        }

        // Handle file picker (already works with webkitdirectory attribute)
        if (event.target && event.target.files) {
            return Array.from(event.target.files);
        }

        // Fallback
        if (event.dataTransfer && event.dataTransfer.files) {
            return Array.from(event.dataTransfer.files);
        }

        return [];
    }

    onDrop(files) {
        const {multiple, setProps} = this.props;
        const newProps = {
            contents: [],
            filename: [],
            last_modified: [],
        };
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = () => {
                /*
                 * I'm not sure if reader.onload will be executed in order.
                 * For example, if the 1st file is larger than the 2nd one,
                 * the 2nd file might load first.
                 */
                newProps.contents.push(reader.result);
                newProps.filename.push(file.name);
                // eslint-disable-next-line no-magic-numbers
                newProps.last_modified.push(file.lastModified / 1000);
                if (newProps.contents.length === files.length) {
                    if (multiple) {
                        setProps(newProps);
                    } else {
                        setProps({
                            contents: newProps.contents[0],
                            filename: newProps.filename[0],
                            last_modified: newProps.last_modified[0],
                        });
                    }
                }
            };
            reader.readAsDataURL(file);
        });
    }

    render() {
        const {
            id,
            children,
            accept,
            disabled,
            disable_click,
            max_size,
            min_size,
            multiple,
            enable_folder_selection,
            className,
            className_active,
            className_reject,
            className_disabled,
            style,
            style_active,
            style_reject,
            style_disabled,
        } = this.props;

        const activeStyle = className_active ? undefined : style_active;
        const disabledStyle = className_disabled ? undefined : style_disabled;
        const rejectStyle = className_reject ? undefined : style_reject;

        // Enable folder selection in file picker when explicitly requested
        // Note: This makes individual files unselectable in the file picker
        const inputProps =
            multiple && enable_folder_selection
                ? {
                      webkitdirectory: 'true',
                      directory: 'true',
                      mozdirectory: 'true',
                  }
                : {};

        return (
            <LoadingElement id={id}>
                <Dropzone
                    onDrop={this.onDrop}
                    accept={accept}
                    disabled={disabled}
                    disableClick={disable_click}
                    maxSize={max_size === -1 ? Infinity : max_size}
                    minSize={min_size}
                    multiple={multiple}
                    inputProps={inputProps}
                    getDataTransferItems={this.getDataTransferItems}
                    className={className}
                    activeClassName={className_active}
                    rejectClassName={className_reject}
                    disabledClassName={className_disabled}
                    style={style}
                    activeStyle={activeStyle}
                    rejectStyle={rejectStyle}
                    disabledStyle={disabledStyle}
                >
                    {children}
                </Dropzone>
            </LoadingElement>
        );
    }
}

Upload.propTypes = propTypes;
