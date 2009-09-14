# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import service
from google.protobuf import service_reflection
from google.protobuf import descriptor_pb2


_LOGINRESPONSE_TYPE = descriptor.EnumDescriptor(
  name='Type',
  full_name='LoginResponse.Type',
  filename='Type',
  values=[
    descriptor.EnumValueDescriptor(
      name='FAILURE', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SUCCESS', index=1, number=1,
      options=None,
      type=None),
  ],
  options=None,
)

_SELECTCITYRESPONSE_TYPE = descriptor.EnumDescriptor(
  name='Type',
  full_name='SelectCityResponse.Type',
  filename='Type',
  values=[
    descriptor.EnumValueDescriptor(
      name='FAILURE', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SUCCESS', index=1, number=1,
      options=None,
      type=None),
  ],
  options=None,
)


_CONTAINER = descriptor.Descriptor(
  name='Container',
  full_name='Container',
  filename='protocol.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='chat', full_name='Container.chat', index=0,
      number=1, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='login', full_name='Container.login', index=1,
      number=2, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='loginResponse', full_name='Container.loginResponse', index=2,
      number=3, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='selectCity', full_name='Container.selectCity', index=3,
      number=4, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='selectCityResponse', full_name='Container.selectCityResponse', index=4,
      number=5, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_CHAT = descriptor.Descriptor(
  name='Chat',
  full_name='Chat',
  filename='protocol.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='message', full_name='Chat.message', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='from', full_name='Chat.from', index=1,
      number=2, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='to', full_name='Chat.to', index=2,
      number=3, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_LOGIN = descriptor.Descriptor(
  name='Login',
  full_name='Login',
  filename='protocol.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='name', full_name='Login.name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='password', full_name='Login.password', index=1,
      number=2, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='regionPassword', full_name='Login.regionPassword', index=2,
      number=3, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_LOGINRESPONSE = descriptor.Descriptor(
  name='LoginResponse',
  full_name='LoginResponse',
  filename='protocol.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='type', full_name='LoginResponse.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
    _LOGINRESPONSE_TYPE,
  ],
  options=None)


_SELECTCITY = descriptor.Descriptor(
  name='SelectCity',
  full_name='SelectCity',
  filename='protocol.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='cityID', full_name='SelectCity.cityID', index=0,
      number=1, type=5, cpp_type=1, label=2,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_SELECTCITYRESPONSE = descriptor.Descriptor(
  name='SelectCityResponse',
  full_name='SelectCityResponse',
  filename='protocol.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='type', full_name='SelectCityResponse.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
    _SELECTCITYRESPONSE_TYPE,
  ],
  options=None)


_CONTAINER.fields_by_name['chat'].message_type = _CHAT
_CONTAINER.fields_by_name['login'].message_type = _LOGIN
_CONTAINER.fields_by_name['loginResponse'].message_type = _LOGINRESPONSE
_CONTAINER.fields_by_name['selectCity'].message_type = _SELECTCITY
_CONTAINER.fields_by_name['selectCityResponse'].message_type = _SELECTCITYRESPONSE
_LOGINRESPONSE.fields_by_name['type'].enum_type = _LOGINRESPONSE_TYPE
_SELECTCITYRESPONSE.fields_by_name['type'].enum_type = _SELECTCITYRESPONSE_TYPE

class Container(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CONTAINER

class Chat(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CHAT

class Login(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LOGIN

class LoginResponse(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LOGINRESPONSE

class SelectCity(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _SELECTCITY

class SelectCityResponse(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _SELECTCITYRESPONSE

