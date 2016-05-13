var express = require('express');
var router = express.Router();
var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var url = 'mongodb://localhost:27017/test'

/* GET home page. */
router.get('/', function(req, res, next) {
  MongoClient.connect(url, function(err, db) {
    if (err) {
      res.render('index', { title: 'Mi Scene', artistObjects: [], errorMessage: err });
    }
    assert.equal(null, err);
    var collection = db.collection('influential_followers');
    collection.find().toArray(function(err, items) {
      if (err) {
        console.log(err);
      }
      else if (items.length) {
        console.log("items: ", items);
        res.render('index', { title: 'Mi Scene', artistObjects: items, errorMessage: null });
      }
      else {
        console.log("No results found");
        res.render('index', { title: 'Mi Scene', artistObjects: [], errorMessage: null });
      }
      console.log("items length: " + items.length);
    });
  });
});

module.exports = router;
