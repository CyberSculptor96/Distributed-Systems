# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: file_system.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11\x66ile_system.proto\"3\n\x11\x43reateFileRequest\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0c\n\x04user\x18\x02 \x01(\t\"%\n\x12\x43reateFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"1\n\x0fReadFileRequest\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0c\n\x04user\x18\x02 \x01(\t\" \n\x10ReadFileResponse\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"@\n\x10WriteFileRequest\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12\x0c\n\x04user\x18\x03 \x01(\t\"$\n\x11WriteFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"3\n\x11\x44\x65leteFileRequest\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0c\n\x04user\x18\x02 \x01(\t\"%\n\x12\x44\x65leteFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\xdf\x01\n\nFileSystem\x12\x35\n\nCreateFile\x12\x12.CreateFileRequest\x1a\x13.CreateFileResponse\x12/\n\x08ReadFile\x12\x10.ReadFileRequest\x1a\x11.ReadFileResponse\x12\x32\n\tWriteFile\x12\x11.WriteFileRequest\x1a\x12.WriteFileResponse\x12\x35\n\nDeleteFile\x12\x12.DeleteFileRequest\x1a\x13.DeleteFileResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'file_system_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_CREATEFILEREQUEST']._serialized_start=21
  _globals['_CREATEFILEREQUEST']._serialized_end=72
  _globals['_CREATEFILERESPONSE']._serialized_start=74
  _globals['_CREATEFILERESPONSE']._serialized_end=111
  _globals['_READFILEREQUEST']._serialized_start=113
  _globals['_READFILEREQUEST']._serialized_end=162
  _globals['_READFILERESPONSE']._serialized_start=164
  _globals['_READFILERESPONSE']._serialized_end=196
  _globals['_WRITEFILEREQUEST']._serialized_start=198
  _globals['_WRITEFILEREQUEST']._serialized_end=262
  _globals['_WRITEFILERESPONSE']._serialized_start=264
  _globals['_WRITEFILERESPONSE']._serialized_end=300
  _globals['_DELETEFILEREQUEST']._serialized_start=302
  _globals['_DELETEFILEREQUEST']._serialized_end=353
  _globals['_DELETEFILERESPONSE']._serialized_start=355
  _globals['_DELETEFILERESPONSE']._serialized_end=392
  _globals['_FILESYSTEM']._serialized_start=395
  _globals['_FILESYSTEM']._serialized_end=618
# @@protoc_insertion_point(module_scope)