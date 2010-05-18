/*
 ###########################################################################
 #
 # This program is part of Zenoss Core, an open source monitoring platform.
 # Copyright (C) 2010, Zenoss Inc.
 #
 # This program is free software; you can redistribute it and/or modify it
 # under the terms of the GNU General Public License version 2 as published by
 # the Free Software Foundation.
 #
 # For complete information please visit: http://www.zenoss.com/oss/
 #
 ###########################################################################
 */

/*
A widget that handles the fact that zProperties can be acquired from parents
in the dmd object hierarchy. The strategy is to use a field set. The title of
the field set is a friendly name for the zProperty (not the z* name). Inside
the field set are two lines. The user selects a line as being the active
setting by clicking on the radio button at the beginning of the row. The top
line has a label that reads 'Set Local Value:', and an appropriate widget for
the type of the zProp (checkbox, textfield, numberfield, or combobox). The 2nd
line states 'Inherit Value' and then indicates the acquired value and the path
of the ancestor from which the value is acquired.

Example usage:

var zMonitor = Ext.create({
    xtype: 'zprop',
    name: 'zMonitor',
    title: _t('Is Monitoring Enabled?'),
    localField: {
        xtype: 'select',
        model: 'local',
        store: [[true, 'Yes'], [false, 'No']],
        value: true
    }
});

zMonitor.setValues({
    isAcquired: false,
    localValue: false,
    acquiredValue: 'No',
    ancestor: '/Processes/Apache'
});

*/

(function() {

Ext.ns('Zenoss.form');


/* A radio button that allows for the boxLabel to be updated.
 */
Zenoss.form.Radio = Ext.extend(Ext.form.Radio, {
    
    setBoxLabel: function(boxLabel) {
        if (this.rendered) {
            this.wrap.down('.x-form-cb-label').update(boxLabel);
        } else {
            this.boxLabel = boxLabel;
        }
    }
    
});

Ext.reg('zradio', Zenoss.form.Radio);


/* A hidden field used internally by the ZProperty fieldset. This hidden field
   overrides getValue to return an object with isAcquired and localValue.
   Introduces the zpropFieldSet config prop which is a reference to the
   ZProperty field set.
 */
Zenoss.form.ZPropHidden = Ext.extend(Ext.form.Hidden, {

    getValue: function() {
        return {
            isAcquired: this.zpropFieldSet.acquiredRadio.getValue(),
            localValue: this.zpropFieldSet.localField.getValue(),
            
            // acquiredValue and ancestor aren't needed by the server, but it
            // is needed by reset which is called when the form is submitted
            acquiredValue: this.zpropFieldSet.acquiredValue,
            ancestor: this.zpropFieldSet.ancestor
        };
    },
    
    setValue: function(values) {
        this.zpropFieldSet.setValues(values);
    },
    
    isDirty: function() {
        return this.zpropFieldSet.acquiredRadio.isDirty() || this.zpropFieldSet.localField.isDirty();
    }

});

Ext.reg('zprophidden', Zenoss.form.ZPropHidden);


/*
A field set that represents a zProperty.

The config parameter passed into the constructor must have a ref. The refOwner
must be the FormPanel.

Additional config keys:
    localField - config for the Ext.form.Field used to input a local setting
    name - string that that is submited to the server as the name
    
New public method:
    setValues - upon context change in the client code, set all the values
                of this composite widget
 */
Zenoss.form.ZProperty = Ext.extend(Ext.form.FieldSet, {

    constructor: function(config) {
        Ext.applyIf(config, {
            hideLabels: true,
            hideBorders: true,
            items: [
                this.getLocalRadioConfig(config.localField),
                this.getAcquiredRadioConfig(),
                this.getHiddenFieldConfig(config.name)
            ]
        });
        Zenoss.form.ZProperty.superclass.constructor.call(this, config);
    },

    setValues: function(values) {
        // values has isAcquired, localValue, acquiredValue, and ancestor
        // localValue is the appropriate type
        // acquiredValue is always a string
        
        // setting the values this away marks the form clean and disables the
        // submit and cancel buttons
        var basicForm = this.refOwner.getForm();
        basicForm.setValues([
            {id: this.localRadio.getName(), value: !values.isAcquired},
            {id: this.localField.getName(), value: values.localValue},
            {id: this.acquiredRadio.getName(), value: values.isAcquired}
        ]);

        // update the boxLabel with the acquiredValue and ancestor
        var boxLabel;
        if ( values.acquiredValue !== null && values.ancestor !== null ) {
            boxLabel = String.format('Inherit Value "{0}" from {1}', values.acquiredValue, values.ancestor);
            this.acquiredRadio.enable();
        } else {
            boxLabel = String.format('Inherit Value');
            this.acquiredRadio.disable();
        }
        this.acquiredRadio.setBoxLabel(boxLabel);
        this.acquiredValue = values.acquiredValue;
        this.ancestor = values.ancestor;
    },

    // private
    getHiddenFieldConfig: function(name) {
        return {
            xtype: 'zprophidden',
            name: name,
            zpropFieldSet: this
        };
    },

    // private
    getAcquiredRadioConfig: function() {
        return {
            xtype: 'zradio',
            ref: 'acquiredRadio',
            boxLabel: 'Inherit Value',
            scope: this,
            handler: function(acquiredRadio, checked) {
                this.localRadio.setValue(!checked);
            }
        };
    },

    //private
    getLocalRadioConfig: function(localField) {
        return {
            xtype: 'panel',
            layout: 'column',
            hideBorders: true,
            defaults: {
                xtype: 'panel',
                layout: 'form',
                hideLabels: true
            },
            items: [{
                width: 107,
                items: [{
                    xtype: 'radio',
                    ref: '../../localRadio',
                    boxLabel: _t('Set Local Value:'),
                    checked: true,
                    scope: this,
                    handler: function(localRadio, checked) {
                        this.acquiredRadio.setValue(!checked);
                    }
                }]
            }, {
                columnWidth: 0.94,
                items: [
                    // Set submitValue to false in case localField has a name  
                    Ext.apply(localField, {
                        ref: '../../localField',
                        submitValue: false,
                        listeners: {
                            scope: this,
                            focus: function() {
                                this.localRadio.setValue(true);
                            }
                        }
                    })
                ]
            }]
        };
    }

});

Ext.reg('zprop', Zenoss.form.ZProperty);


// A simple ComboBox that behaves like an HTML select tag
Zenoss.form.Select = Ext.extend(Ext.form.ComboBox, {
    
    constructor: function(config){
        Ext.applyIf(config, {
            allowBlank: false,
            triggerAction: 'all',
            typeAhead: false,
            forceSelection: true
        });
        Zenoss.form.Select.superclass.constructor.call(this, config);
    }
    
});

Ext.reg('select', Zenoss.form.Select);


})();