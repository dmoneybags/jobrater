import { stringify } from "querystring";
import { json } from "stream/consumers";

export class LocationObject {
    /**
     * Class LocationObject
     * 
     * Simple struct representing address data
     * 
     * No support for latitude and longitude currently but coming soon
     * 
     * @property {string} addressStr - the street number and name IE: 112 Adrian pl
     * @property {string} city - the city of the location IE: Los Gatos
     * @property {string} zipCode - the zip code of the location IE: 95032
     * @property {string} stateCode - the stateCode of the location IE: CA
     * @property {number} latitude - the latitude of the location
     * @property {number} longitude - the longitude of the location
     */
    addressStr : string;
    city: string;
    zipCode: string;
    stateCode: string;
    latitude: number | null;
    longitude: number | null;
    constructor(addressStr: string, city: string, zipCode: string, stateCode: string, latitude: number | null, 
        longitude: number | null
    ){
        this.addressStr = addressStr;
        this.city = city;
        this.zipCode = zipCode;
        this.stateCode = stateCode;
        this.latitude = latitude;
        this.longitude = longitude;
    }
}
/**
 * class LocationObjectFactory
 * 
 * A collection of functions that create location objects from other structs (JSON)
 */
export class LocationObjectFactory {
    /**
     * generateLocationFromJson
     * 
     * generates a location object from a json response from the server
     * 
     * @param {Record<string, any>} json_object 
     * @returns {LocationObject}
     */
    static generateLocationFromJson(json_object:Record<string, any>): LocationObject {
        if (json_object["addressStr"] && typeof json_object["addressStr"] !== "string"){throw new TypeError("Invalid data passed to contructor: " + json_object)}
        const addressStr: string = json_object["addressStr"];
        const city: string = json_object["city"];
        const zipCode: string = json_object["zipCode"];
        const stateCode: string = json_object["stateCode"];
        const latitude: number | null = json_object["latitude"] ? json_object["latitude"] : null;
        const longitude: number | null = json_object["longitude"] ? json_object["longitude"] : null;
        return new LocationObject(addressStr, city, zipCode, stateCode, latitude, longitude);
    }
}