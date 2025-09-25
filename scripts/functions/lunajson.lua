local newdecoder = require 'functions.lunajson.decoder'
local newencoder = require 'functions.lunajson.encoder'
local sax = require 'functions.lunajson.sax'
-- If you need multiple contexts of decoder and/or encoder,
-- you can require lunajson.decoder and/or lunajson.encoder directly.
return {
	decode = newdecoder(),
	encode = newencoder(),
	newparser = sax.newparser,
	newfileparser = sax.newfileparser,
}