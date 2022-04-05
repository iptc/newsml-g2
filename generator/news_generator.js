'use strict';

class NewsGenerator extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            output: '',
            bodyformat: 'nitf',
            qcodeuri: 'qcodes',
            itemclass: 'text',
            pubstatus: 'usable',
            urgency: '',
            genre: '',
            byline: '',
            language: '',
            headline: '',
            medtop: [],
            subheadline: '',
            provider: '',
            profile: '',
            copyrightholder: '',
            copyrightnotice: '',
            usageterms: '',
            slugline: '',
            bodytext: '',
            location: '',
            altid_name: '',
            altid_value: '',
            ednote: ''
        };
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    componentDidMount() {
        $('[data-toggle="tooltip"]').tooltip();
        this.refreshOutput();
    }
    componentDidUpdate() {
        $('[data-toggle="tooltip"]').tooltip();
    }
    refreshOutput() {    
        var output = this.getNewsOutput();
        this.setState({output: output});
    }
    getNewsOutput() {
        var xmlDoc = document.implementation.createDocument(
            'http://iptc.org/std/nar/2006-10-01/', 'newsItem', null
        );
        var newsItem = xmlDoc.documentElement;
        var todaysDate = new Date().toISOString().slice(0, 10);
        var slugline = this.state.slugline;
        var slugforguid;
        if (slugline) {
            slugforguid = slugline.toUpperCase();
        } else {
            slugforguid = "SLUGLINE";
        }
        newsItem.setAttribute('guid', 'urn:newsml:testnewsprovider.com:'+todaysDate+':'+slugforguid);
        newsItem.setAttribute('version', '1');
        newsItem.setAttribute('standard', 'NewsML-G2');
        newsItem.setAttribute('standardversion', '2.30');
        newsItem.setAttribute('conformance', 'power');
        if (this.state.qcodeuri == 'qcodes') {
            var catalogRef = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'catalogRef');
            catalogRef.setAttribute('href', 'http://www.iptc.org/std/catalog/catalog.IPTC-G2-Standards_37.xml');
            xmlDoc.documentElement.appendChild(catalogRef);
        }

        /* rightsInfo */
        if (this.state.copyrightholder !== '' || this.state.copyrightnotice !== '' || this.state.usageterms !== '') {
            var rightsInfo = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'rightsInfo');
            if (this.state.copyrightholder !== '') {
                var copyrightHolder = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'copyrightHolder');
                var copyrightHolderName = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                copyrightHolderName.innerHTML = this.state.copyrightholder;
                copyrightHolder.appendChild(copyrightHolderName);
                rightsInfo.appendChild(copyrightHolder);
            }
            if (this.state.copyrightnotice !== '') {
                var copyrightNotice = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'copyrightNotice');
                copyrightNotice.innerHTML = this.state.copyrightnotice;
                rightsInfo.appendChild(copyrightNotice);
            }
            if (this.state.usageterms !== '') {
                var usageTerms = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'usageTerms');
                usageTerms.innerHTML = this.state.usageterms;
                rightsInfo.appendChild(usageTerms);
            }
            xmlDoc.documentElement.appendChild(rightsInfo);
        }

        /* itemMeta */
        var itemMetaElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'itemMeta');
        /* itemMeta/itemClass is required for NewsML-G2 */
        var itemClassElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'itemClass');
        if (this.state.qcodeuri == 'qcodes') {
            itemClassElem.setAttribute('qcode', 'ninat:'+this.state.itemclass);
        } else {
            itemClassElem.setAttribute('uri', 'http://cv.iptc.org/newscodes/ninat/'+this.state.itemclass);
        }
        itemMetaElem.appendChild(itemClassElem);
        /* itemMeta/provider is required for NewsML-G2 */
        var providerElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'provider');
        var providerNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
        providerNameElem.innerHTML = this.state.provider;
        providerElem.appendChild(providerNameElem);
        itemMetaElem.appendChild(providerElem);
        var dateISOString = new Date().toISOString();
        var versionCreatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'versionCreated');
        versionCreatedElem.innerHTML = dateISOString;
        itemMetaElem.appendChild(versionCreatedElem);
        var firstCreatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'firstCreated');
        firstCreatedElem.innerHTML = dateISOString;
        itemMetaElem.appendChild(firstCreatedElem);
        var pubStatusElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'pubStatus');
        if (this.state.qcodeuri == 'qcodes') {
            pubStatusElem.setAttribute('qcode', 'stat:'+this.state.pubstatus);
        } else {
            pubStatusElem.setAttribute('uri', 'http://cv.iptc.org/newscodes/stat/'+this.state.pubstatus);
        }
        itemMetaElem.appendChild(pubStatusElem);
        var generatorElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'generator');
        generatorElem.innerHTML = 'IPTC NewsML-G2 Generator v0.9';
        itemMetaElem.appendChild(generatorElem);
        if (this.state.profile !== '') {
            var profileElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'profile');
            profileElem.innerHTML = this.state.profile;
            itemMetaElem.appendChild(profileElem);
        }
        if (this.state.ednote !== '') {
            var edNoteElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'edNote');
            edNoteElem.innerHTML = this.state.ednote;
            itemMetaElem.appendChild(edNoteElem);
        }
        xmlDoc.documentElement.appendChild(itemMetaElem);

        /* contentMeta */
        if (this.state.urgency !== '' || this.state.location !== '' || this.state.byline !== '' || this.state.altid_name !== '' || this.state.altid_value !== '' || this.state.language !== '' || this.state.genre !== '' || this.state.medtop.length != 0 || this.state.headline  !== ''|| this.state.slugline !== '') {
            var contentMetaElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'contentMeta');
            if (this.state.urgency) {
                var urgencyElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'urgency');
                urgencyElem.innerHTML = this.state.urgency;
                contentMetaElem.appendChild(urgencyElem);
            }
            /* removed after decision at NAR meeting on 2021-04-23
            var contentCreatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'contentCreated');
            contentCreatedElem.innerHTML = dateISOString;
            contentMetaElem.appendChild(contentCreatedElem);
            var contentModifiedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'contentModified');
            contentModifiedElem.innerHTML = dateISOString;
            contentMetaElem.appendChild(contentModifiedElem);
            */
            if (this.state.location) {
                var locatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'located');
                var locatedNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                locatedNameElem.innerHTML = this.state.location;
                locatedElem.appendChild(locatedNameElem);
                contentMetaElem.appendChild(locatedElem);
            }
            /* removed by agreement at NAR meeting 2021-04-23 
            if (this.state.byline) {
                var creatorElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'creator');
                var creatorNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                creatorNameElem.innerHTML = this.state.byline;
                creatorElem.appendChild(creatorNameElem);
                contentMetaElem.appendChild(creatorElem);
            } */
            /* TODO: validate the altid_name to be a well-formed qcode (e.g. no spaces) */
            if (this.state.altid_name && this.state.altid_value) {
                var altIdElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'altId');
                if (this.state.qcodeuri == 'qcodes') {
                    altIdElem.setAttribute('type', 'examplealtid:'+this.state.altid_name)
                } else {
                    altIdElem.setAttribute('typeuri', 'http://cv.iptc.org/example/'+this.state.altid_name);
                }
                altIdElem.innerHTML = this.state.altid_value;
                contentMetaElem.appendChild(altIdElem);
            }
            if (this.state.language) {
                var languageElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'language');
                languageElem.setAttribute('tag', this.state.language);
                contentMetaElem.appendChild(languageElem);
            }
            if (this.state.genre) {
                var genreElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'genre');
                if (this.state.qcodeuri == 'qcodes') {
                    genreElem.setAttribute('qcode', 'genre:'+this.state.genre);
                } else {
                    genreElem.setAttribute('uri', 'http://cv.iptc.org/genre/'+this.state.genre);
                }
                contentMetaElem.appendChild(genreElem);
            }
            if (this.state.medtop) {
                for (var value of this.state.medtop) {
                    var subjectElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'subject');
                    if (this.state.qcodeuri == 'qcodes') {
                        subjectElem.setAttribute('qcode', 'medtop:'+value);
                    } else {
                        subjectElem.setAttribute('uri', 'http://cv.iptc.org/medtop/'+value);
                    }
                    contentMetaElem.appendChild(subjectElem);
                }
            }
            if (this.state.byline) {
                var byElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'by');
                byElem.innerHTML = this.state.byline;
                contentMetaElem.appendChild(byElem);
            }
            if (this.state.slugline) {
                var sluglineElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'slugline');
                sluglineElem.innerHTML = this.state.slugline;
                contentMetaElem.appendChild(sluglineElem);
            }
            if (this.state.headline) {
                var headlineElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'headline');
                headlineElem.innerHTML = document.indata.headline.value;
                contentMetaElem.appendChild(headlineElem);
            }
            xmlDoc.documentElement.appendChild(contentMetaElem);
        }

        /* contentSet */
        if (this.state.ednote || this.state.copyrightholder || this.state.headline || this.state.subheadline || this.state.bodytext) {
            var contentSetElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'contentSet');
            var inlineXMLElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'inlineXML');
            var bodyns = (this.state.bodyformat == 'nitf')
                         ? 'http://iptc.org/std/NITF/2006-10-18/'
                         : 'http://www.w3.org/1999/xhtml';
            var bodyWrapperElem;
            if (this.state.bodyformat == 'nitf') {
                inlineXMLElem.setAttribute('contenttype', 'application/nitf+xml');
                /* TODO: add more G2 fields to NITF section: copyright */
                bodyWrapperElem = document.createElementNS(bodyns, 'nitf');
                var nitfHeadElem = document.createElementNS(bodyns, 'head');
                var nitfDocdataElem = document.createElementNS(bodyns, 'docdata');
                if (this.state.ednote) {
                    var nitfDocdataEdMsgElem = document.createElementNS(bodyns, 'ed-msg');
                    nitfDocdataEdMsgElem.setAttribute('info', this.state.ednote.replace(/(\r\n|\n|\r)/gm," "));
                    nitfDocdataElem.appendChild(nitfDocdataEdMsgElem);
                }
                if (this.state.copyrightholder) {
                    var nitfDocdataDocCopyrightElem = document.createElementNS(bodyns, 'doc.copyright');
                    nitfDocdataDocCopyrightElem.setAttribute('holder', this.state.copyrightholder);
                    nitfDocdataElem.appendChild(nitfDocdataDocCopyrightElem);
                }
                nitfHeadElem.appendChild(nitfDocdataElem);
                bodyWrapperElem.appendChild(nitfHeadElem);
                if (this.state.headline || this.state.subheadline || this.state.byline || this.state.bodytext) {
                    var nitfBodyElem = document.createElementNS(bodyns, 'body');
                    if (this.state.bodyformat == 'nitf') {
                        var nitfBodyHeadElem = document.createElementNS(bodyns, 'body.head');
                        var nitfBodyHeadHedlineElem = document.createElementNS(bodyns, 'hedline');
                        var nitfBodyHeadHedlineHl1Elem = document.createElementNS(bodyns, 'hl1');
                        nitfBodyHeadHedlineHl1Elem.innerHTML = this.state.headline;
                        nitfBodyHeadHedlineElem.appendChild(nitfBodyHeadHedlineHl1Elem);
                        if (this.state.subheadline) {
                            var nitfBodyHeadHedlineHl2Elem = document.createElementNS(bodyns, 'hl2');
                            nitfBodyHeadHedlineHl2Elem.innerHTML = this.state.subheadline;
                            nitfBodyHeadHedlineElem.appendChild(nitfBodyHeadHedlineHl2Elem);
                        }
                        nitfBodyHeadElem.appendChild(nitfBodyHeadHedlineElem);
                        nitfBodyElem.appendChild(nitfBodyHeadElem);
                    } else /* xhtml */ {
                    }
                    if (this.state.byline) {
                        var nitfBodyHeadBylineElem = document.createElementNS(bodyns, 'byline');
                        nitfBodyHeadBylineElem.innerHTML = this.state.byline;
                        nitfBodyHeadElem.appendChild(nitfBodyHeadBylineElem);
                    }
                    if (this.state.bodytext) {
                        var nitfBodyContentElem = document.createElementNS(bodyns, 'body.content');
                        var nitfBodyContentPElem = document.createElementNS(bodyns, 'p');
                        nitfBodyContentPElem.innerHTML = this.state.bodytext;
                        nitfBodyContentElem.appendChild(nitfBodyContentPElem);
                        nitfBodyElem.appendChild(nitfBodyContentElem);
                    }
                    bodyWrapperElem.appendChild(nitfBodyElem);
                }
            } else /* xhtml */ {
                inlineXMLElem.setAttribute('contenttype', 'application/xhtml+xml');
                bodyWrapperElem = document.createElementNS(bodyns, 'html');
                if (this.state.headline) {
                    var bodyHeadElem = document.createElementNS(bodyns, 'head');
                    var bodyTitleElem = document.createElementNS(bodyns, 'title');
                    bodyTitleElem.innerHTML = this.state.headline;
                    bodyHeadElem.appendChild(bodyTitleElem);
                    bodyWrapperElem.appendChild(bodyHeadElem);
                }
                if (this.state.bodytext) {
                    var xhtmlBodyElem = document.createElementNS(bodyns, 'body');
                    /** removed by agreement at NAR meeting 2021-04-23
                    if (this.state.headline) {
                        var xhtmlBodyh1Elem = document.createElementNS(bodyns, 'h1');
                        xhtmlBodyh1Elem.innerHTML = this.state.headline;
                        xhtmlBodyElem.appendChild(xhtmlBodyh1Elem);
                    } */
                    var xhtmlpElem = document.createElementNS(bodyns, 'p');
                    xhtmlpElem.innerHTML = this.state.bodytext;
                    xhtmlBodyElem.appendChild(xhtmlpElem);
                    bodyWrapperElem.appendChild(xhtmlBodyElem);
                }
            }
            inlineXMLElem.appendChild(bodyWrapperElem);
            contentSetElem.appendChild(inlineXMLElem);
            xmlDoc.documentElement.appendChild(contentSetElem);
        }
        /* turn XML object into string */
        var serializer = new XMLSerializer();
        var xmlString = serializer.serializeToString(xmlDoc);
        xmlString = this.xmlpretty(xmlString, 1);
        const xmlDecl = '<?xml version="1.0" encoding="UTF-8"?>'
        var xmlDocAsString =  xmlDecl + '\n' + xmlString.toString();
        return xmlDocAsString;
    }
    handleSubmit(event) {
        /* there's no submit button but just in case some automatic feature tries to submit the form... */
        event.preventDefault();
    }
    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked
            : target.type === 'select-multiple' ? [...target.selectedOptions].map(o => o.value)
            : target.value;
        const name = target.name;
        // setState is asynchronous so we update the output after completion using the callback
        this.setState({
            [name]: value
        }, this.refreshOutput);
    }
    copyToClipboard = (e) => {
        this.textArea.select();
        document.execCommand('copy');
        // This is just personal preference.
        // I prefer to not show the whole text area selected.
        e.target.focus();
        this.setState({ copySuccess: 'Copied!' });
        e.preventDefault();
    };
    // used by xmlpretty below
    createShiftArr(step) {
        var space = '    ';
        if ( isNaN(parseInt(step)) ) {  // argument is string
            space = step;
        } else { // argument is integer
            switch(step) {
                case 1: space = '  '; break;
                case 2: space = '    '; break;
                case 3: space = '      '; break;
                case 4: space = '        '; break;
                case 5: space = '          '; break;
                case 6: space = '            '; break;
                case 7: space = '              '; break;
                case 8: space = '                '; break;
                case 9: space = '                  '; break;
                case 10: space = '                    '; break;
                case 11: space = '                      '; break;
                case 12: space = '                        '; break;
            }
        }

        var shift = ['\n']; // array of shifts
        for(var ix=0;ix<100;ix++){
            shift.push(shift[ix]+space);
        }
        return shift;
    }
    xmlpretty(text,step) {
        var shift = this.createShiftArr(step);
        var ar = text.replace(/>\s{0,}</g,"><")
                     .replace(/</g,"~::~<")
                     .replace(/\s*xmlns\:/g,"~::~xmlns:")
                     .replace(/\s*xmlns\=/g,"~::~xmlns=")
                     .split('~::~'),
            len = ar.length,
            inComment = false,
            deep = 0,
            str = '',
            ix = 0,
            shift = step ? this.createShiftArr(step) : shift;

        for(ix=0;ix<len;ix++) {
            // start comment or <![CDATA[...]]> or <!DOCTYPE //
            if(ar[ix].search(/<!/) > -1) {
                str += shift[deep]+ar[ix];
                inComment = true;
                // end comment  or <![CDATA[...]]> //
                if(ar[ix].search(/-->/) > -1 || ar[ix].search(/\]>/) > -1 || ar[ix].search(/!DOCTYPE/) > -1 ) {
                    inComment = false;
                }
            } else
            // end comment  or <![CDATA[...]]> //
            if(ar[ix].search(/-->/) > -1 || ar[ix].search(/\]>/) > -1) {
                str += ar[ix];
                inComment = false;
            } else
            // <elm></elm> //
            if( /^<\w/.exec(ar[ix-1]) && /^<\/\w/.exec(ar[ix]) &&
                /^<[\w:\-\.\,]+/.exec(ar[ix-1]) == /^<\/[\w:\-\.\,]+/.exec(ar[ix])[0].replace('/','')) {
                str += ar[ix];
                if(!inComment) deep--;
            } else
             // <elm> //
            if(ar[ix].search(/<\w/) > -1 && ar[ix].search(/<\//) == -1 && ar[ix].search(/\/>/) == -1 ) {
                str = !inComment ? str += shift[deep++]+ar[ix] : str += ar[ix];
            } else
             // <elm>...</elm> //
            if(ar[ix].search(/<\w/) > -1 && ar[ix].search(/<\//) > -1) {
                str = !inComment ? str += shift[deep]+ar[ix] : str += ar[ix];
            } else
            // </elm> //
            if(ar[ix].search(/<\//) > -1) {
                str = !inComment ? str += shift[--deep]+ar[ix] : str += ar[ix];
            } else
            // <elm/> //
            if(ar[ix].search(/\/>/) > -1 ) {
                str = !inComment ? str += shift[deep]+ar[ix] : str += ar[ix];
            } else
            // <? xml ... ?> //
            if(ar[ix].search(/<\?/) > -1) {
                str += shift[deep]+ar[ix];
            } else
            // xmlns //
            if( ar[ix].search(/xmlns\:/) > -1  || ar[ix].search(/xmlns\=/) > -1) {
                str += shift[deep]+ar[ix];
            }

            else {
                str += ar[ix];
            }
        }

        return  (str[0] == '\n') ? str.slice(1) : str;
    }

    render() {
        var outputtext = "View the generated NewsML-G2";
        return (
<form name="indata" method="post" onSubmit={this.handleSubmit}>
    <div className="row">
        <div className="col">
            <legend>Enter news item content</legend>
            <div className="form-row">
                <div className="col form-group">
                    <label htmlFor="itemclass">Item type <i className="fas fa-info-circle" data-toggle="tooltip" data-placement="top" title='Also known as "news nature"' /></label>
                    <select className="form-control form-control-sm" id="itemclass" name="itemclass" size="1" width="3" value={this.state.itemclass} onChange={this.handleInputChange} tabIndex="1">
                        <option value="text"> Text </option>
                        <option value="audio"> Audio </option>
                        <option value="video"> Video </option>
                        <option value="picture"> Picture </option>
                        <option value="graphic"> Graphic </option>
                        <option value="composite"> Composite </option>
                    </select>
                </div>
                <div className="col form-group">
                    <label htmlFor="pubstatus">Publication status</label>
                    <select className="form-control form-control-sm" id="pubstatus" name="pubstatus" size="1" width="3" value={this.state.pubstatus} onChange={this.handleInputChange} tabIndex="2">
                        <option value="usable"> Usable </option>
                        <option value="cancelled"> Cancelled </option>
                        <option value="withheld"> Withheld </option>
                    </select>
                </div>
                <div className="col form-group">
                    <label htmlFor="urgency">Urgency</label>
                    <select className="form-control form-control-sm" id="urgency" name="urgency" size="1" width="3" value={this.state.urgency} onChange={this.handleInputChange} tabIndex="3">
                        <option value=""> (None) </option>
                        <option value="1"> 1 </option>
                        <option value="2"> 2 </option>
                        <option value="3"> 3 </option>
                        <option value="4"> 4 </option>
                        <option value="5"> 5 </option>
                        <option value="6"> 6 </option>
                        <option value="7"> 7 </option>
                        <option value="8"> 8 </option>
                        <option value="9"> 9 </option>
                    </select>
                </div>
                <div className="col form-group">
                    <label htmlFor="genre">Genre <i className="fas fa-info-circle" data-toggle="tooltip" data-placement="top" title='Values are taken from https://cv.iptc.org/newscodes/genre' /></label>
                    <div className="col-sm-10">
                    <select className="form-control form-control-sm" id="genre" name="genre" size="1" width="3" value={this.state.genre} onChange={this.handleInputChange} tabIndex="4">
                        <option value=""> (None) </option>
                        <option value="Actuality"> Actuality </option>
                        <option value="Advice"> Advice </option>
                        <option value="Advisory"> Advisory </option>
                        <option value="Almanac"> Almanac </option>
                        <option value="Analysis"> Analysis </option>
                        <option value="Archive_material"> Archive material </option>
                        <option value="Background"> Background </option>
                        <option value="Biography"> Biography </option>
                        <option value="Birth_Announcement"> Birth Announcement </option>
                        <option value="Current"> Current </option>
                        <option value="Curtain_Raiser"> Curtain Raiser </option>
                        <option value="Daybook"> Daybook </option>
                        <option value="Exclusive"> Exclusive </option>
                        <option value="Feature"> Feature </option>
                        <option value="Fixture"> Fixture </option>
                        <option value="Forecast"> Forecast </option>
                        <option value="From_the_Scene"> From the Scene </option>
                        <option value="History"> History </option>
                        <option value="Horoscope"> Horoscope </option>
                        <option value="Interview"> Interview </option>
                        <option value="Listing_of_facts"> Listing of facts </option>
                        <option value="Music"> Music </option>
                        <option value="Obituary"> Obituary </option>
                        <option value="Opinion"> Opinion </option>
                        <option value="Polls_and_Surveys"> Polls and Surveys </option>
                        <option value="Press_Release"> Press Release </option>
                        <option value="Press-Digest"> Press-Digest </option>
                        <option value="Profile"> Profile </option>
                        <option value="Program"> Program </option>
                        <option value="Question_and_Answer_Session"> Question and Answer Session </option>
                        <option value="Quote"> Quote </option>
                        <option value="Raw_Sound"> Raw Sound </option>
                        <option value="Response_to_a_Question"> Response to a Question </option>
                        <option value="Results_Listings_and_Statistics"> Results Listings and Statistics </option>
                        <option value="Retrospective"> Retrospective </option>
                        <option value="Review"> Review </option>
                        <option value="Scener"> Scener </option>
                        <option value="Side_bar_and_supporting_information"> Side bar and supporting information </option>
                        <option value="Special_Report"> Special Report </option>
                        <option value="Summary"> Summary </option>
                        <option value="Synopsis"> Synopsis </option>
                        <option value="Text_only"> Text only </option>
                        <option value="Transcript_and_Verbatim"> Transcript and Verbatim </option>
                        <option value="Update"> Update </option>
                        <option value="Voicer"> Voicer </option>
                        <option value="Wrap"> Wrap </option>
                        <option value="Wrapup"> Wrapup </option>
                    </select>
                    </div>
                </div>
                <div className="col form-group">
                    <label htmlFor="language">Language <i className="fas fa-info-circle" data-toggle="tooltip" data-placement="top" title='Language of news item content' /></label>
                    <select className="form-control form-control-sm" id="language" name="language" size="1" width="3" value={this.state.language} onChange={this.handleInputChange} tabIndex="5">
                        <option value="">(None)</option>
                        <option value="af">Afrikaans</option>
                        <option value="sq">Albanian</option>
                        <option value="ar">Arabic</option>
                        <option value="hy">Armenian</option>
                        <option value="eu">Basque</option>
                        <option value="bn">Bengali</option>
                        <option value="bg">Bulgarian</option>
                        <option value="ca">Catalan</option>
                        <option value="km">Cambodian</option>
                        <option value="zh">Chinese (Mandarin)</option>
                        <option value="hr">Croatian</option>
                        <option value="cs">Czech</option>
                        <option value="da">Danish</option>
                        <option value="nl">Dutch</option>
                        <option value="en">English</option>
                        <option value="et">Estonian</option>
                        <option value="fj">Fijian</option>
                        <option value="fi">Finnish</option>
                        <option value="fr">French</option>
                        <option value="ka">Georgian</option>
                        <option value="de">German</option>
                        <option value="el">Greek</option>
                        <option value="gu">Gujarati</option>
                        <option value="he">Hebrew</option>
                        <option value="hi">Hindi</option>
                        <option value="hu">Hungarian</option>
                        <option value="is">Icelandic</option>
                        <option value="id">Indonesian</option>
                        <option value="ga">Irish</option>
                        <option value="it">Italian</option>
                        <option value="ja">Japanese</option>
                        <option value="jw">Javanese</option>
                        <option value="ko">Korean</option>
                        <option value="la">Latin</option>
                        <option value="lv">Latvian</option>
                        <option value="lt">Lithuanian</option>
                        <option value="mk">Macedonian</option>
                        <option value="ms">Malay</option>
                        <option value="ml">Malayalam</option>
                        <option value="mt">Maltese</option>
                        <option value="mi">Maori</option>
                        <option value="mr">Marathi</option>
                        <option value="mn">Mongolian</option>
                        <option value="ne">Nepali</option>
                        <option value="no">Norwegian</option>
                        <option value="fa">Persian</option>
                        <option value="pl">Polish</option>
                        <option value="pt">Portuguese</option>
                        <option value="pa">Punjabi</option>
                        <option value="qu">Quechua</option>
                        <option value="ro">Romanian</option>
                        <option value="ru">Russian</option>
                        <option value="sm">Samoan</option>
                        <option value="sr">Serbian</option>
                        <option value="sk">Slovak</option>
                        <option value="sl">Slovenian</option>
                        <option value="es">Spanish</option>
                        <option value="sw">Swahili</option>
                        <option value="sv">Swedish</option>
                        <option value="ta">Tamil</option>
                        <option value="tt">Tatar</option>
                        <option value="te">Telugu</option>
                        <option value="th">Thai</option>
                        <option value="bo">Tibetan</option>
                        <option value="to">Tonga</option>
                        <option value="tr">Turkish</option>
                        <option value="uk">Ukranian</option>
                        <option value="ur">Urdu</option>
                        <option value="uz">Uzbek</option>
                        <option value="vi">Vietnamese</option>
                        <option value="cy">Welsh</option>
                        <option value="xh">Xhosa</option>
                    </select>
                </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="headline">Headline</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="headline" name="headline" size="40" title="Headline" value={this.state.headline} onChange={this.handleInputChange}  tabIndex="6" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="subheadline">Subheadline</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="subheadline" name="subheadline" size="40" title="Subheadline" value={this.state.subheadline} onChange={this.handleInputChange} tabIndex="8" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="provider">Provider</label>
                    <div className="col-sm-4">
                        <input className="form-control form-control-sm" type="text" id="provider" name="provider" size="25" title="Abbreviation of provider of information." value={this.state.provider} onChange={this.handleInputChange} tabIndex="9" />
                    </div>
                    <label className="col-sm-2 col-form-label" htmlFor="profile">Profile</label>
                    <div className="col-sm-4">
                        <input className="form-control form-control-sm" type="text" id="profile" name="profile" size="25" title="Profile (if exists)." value={this.state.profile} onChange={this.handleInputChange} tabIndex="10" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="copyrightholder">Copyright Holder</label>
                    <div className="col-sm-9">
                        <input className="form-control form-control-sm" type="text" id="copyrightholder" name="copyrightholder" size="25" title="Copyright holder for this item." value={this.state.copyrightholder} onChange={this.handleInputChange} tabIndex="11" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="copyrightnotice">Copyright Notice</label>
                    <div className="col-sm-9"> <input className="form-control form-control-sm" type="text" id="copyrightnotice" name="copyrightnotice" size="25" title="Copyright notice for this item." value={this.state.copyrightnotice} onChange={this.handleInputChange} tabIndex="12" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="usageterms">Usage Terms</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="usageterms" name="usageterms" size="40" title="Special usage terms" value={this.state.usageterms} onChange={this.handleInputChange} tabIndex="13" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="slugline">Slugline</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="slugline" name="slugline" size="40" title="Slugline" value={this.state.slugline} onChange={this.handleInputChange}  tabIndex="14" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="medtop">IPTC Media Topic(s)</label>
                    <div className="col-sm-9">
                        <select className="form-control form-control-sm" id="medtop" name="medtop" size="5" width="25" multiple={true} title="Select the applicable codes." value={this.state.medtop} onChange={this.handleInputChange} tabIndex="7">
                            <option value="01000000">Arts, culture, entertainment and media</option>
                            <option value="02000000">Crime, law and justice</option>
                            <option value="03000000">Disaster and accident</option>
                            <option value="04000000">Economy, business and finance</option>
                            <option value="05000000">Education</option>
                            <option value="06000000">Environmental issues</option>
                            <option value="07000000">Health</option>
                            <option value="08000000">Human interest</option>
                            <option value="09000000">Labour</option>
                            <option value="10000000">Lifestyle and leisure</option>
                            <option value="11000000">Politics</option>
                            <option value="12000000">Religion and belief</option>
                            <option value="13000000">Science and technology</option>
                            <option value="14000000">Social issues</option>
                            <option value="15000000">Sport</option>
                            <option value="16000000">Unrest, conflict and war</option>
                            <option value="17000000">Weather</option>
                        </select>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="byline">Byline</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="byline" name="byline" size="40" title="Byline" value={this.state.byline} onChange={this.handleInputChange} tabIndex="16"/>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="location">Location</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="location" name="location" size="40" title="Location" value={this.state.location} onChange={this.handleInputChange} tabIndex="17"/>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="altid_name">Alternative id: Name</label>
                    <div className="col-sm-4">
                        <input className="form-control form-control-sm" type="text" id="altid_name" name="altid_name" size="15" title="Altid_name" value={this.state.altid_name} onChange={this.handleInputChange} tabIndex="18" />
                    </div>
                    <label className="col-sm-1 col-form-label" htmlFor="altid_value">Value</label>
                    <div className="col-sm-4">
                        <input className="form-control form-control-sm" type="text" id="altid_value" name="altid_value" size="15" title="Altid_value" value={this.state.altid_value} onChange={this.handleInputChange} tabIndex="19" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="bodytext">Body text</label>
                    <div className="col-sm-10">
                        <textarea className="form-control form-control-sm" id="bodytext" name="bodytext" rows="5" wrap="virtual" cols="60" value={this.state.bodytext} onChange={this.handleInputChange} tabIndex="15"></textarea>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="ednote">Editorial notes</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="ednote" name="ednote" size="30" title="Editorial notes" value={this.state.ednote} onChange={this.handleInputChange} tabIndex="20" />
                    </div>
                </div>
        </div>
        <div className="col">
            <div className="outputbox">
                <legend>{outputtext} <small><a href="#" onClick={this.copyToClipboard}>Copy to clipboard <i className="fas fa-copy" /></a></small></legend>
                <div className="form-row">
                    <div className="col-sm-6">
                        Choose body text format:
                    </div>
                    <div className="col-sm-5">
                        <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" defaultChecked name="bodyformat" id="nitf" value="nitf" title="Body text format - NITF" onChange={this.handleInputChange} tabIndex="21" />&nbsp;
                            <label className="form-check-label" htmlFor="nitf">NITF</label>
                        </div>
                        <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" name="bodyformat" id="xhtml" value="xhtml" title="Body text format - XHTML" onChange={this.handleInputChange} tabIndex="22" />&nbsp;
                            <label className="form-check-label" htmlFor="xhtml">XHTML</label>
                        </div>
                    </div>
                </div>
                <div className="form-row">
                    <div className="col-sm-6">
                        Choose controlled value display format:
                    </div>
                    <div className="col-sm-5">
                        <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" defaultChecked name="qcodeuri" id="qcodes" value="qcodes" title="QCodes" onChange={this.handleInputChange} tabIndex="23" />&nbsp;
                            <label className="form-check-label" htmlFor="qcodes">QCodes</label>
                        </div>
                        <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" name="qcodeuri" id="uris" value="uris" title="URIs" onChange={this.handleInputChange} tabIndex="24" />&nbsp;
                            <label className="form-check-label" htmlFor="uris">URIs</label>
                        </div>
                    </div>
                </div>
                <textarea className="form-control" name="output" style={{'height': '100%', 'fontSize': '12px'}} rows="40" tabIndex="25" value={this.state.output} ref={(textarea) => this.textArea = textarea} readOnly></textarea>
            </div>
        </div>
    </div>
</form>
        )
    }
}

const domContainer = document.querySelector('#reactcontainer');
ReactDOM.render(<NewsGenerator/>, domContainer);
