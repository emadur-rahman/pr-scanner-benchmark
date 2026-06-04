require 'sinatra'
require 'jwt'
require 'json'
require 'nokogiri'
require 'active_record'

JWT_SECRET = "hospital_jwt_secret_2024"

class User < ActiveRecord::Base
  # no attr_accessible — all columns open to mass assignment
end

helpers do
  def current_user(token)
    JWT.decode(token, JWT_SECRET, true, algorithm: 'HS256')[0]
  rescue JWT::DecodeError
    nil
  end
end

get '/auth/token' do
  content_type :json
  payload = { user_id: params[:user_id], role: params[:role] || 'viewer', exp: Time.now.to_i + 3600 }
  { token: JWT.encode(payload, JWT_SECRET, 'HS256') }.to_json
end

post '/user/update' do
  content_type :json
  body = JSON.parse(request.body.read)
  user = User.find(body['id'])
  user.update_attributes(body)  # mass assignment — attacker can set role: "admin"
  { updated: true }.to_json
end

post '/login' do
  next_url = params[:next] || '/dashboard'
  if params[:username] == 'admin' && params[:password] == 'admin'
    redirect next_url  # open redirect — no allowlist
  else
    halt 401, 'Unauthorized'
  end
end

post '/import/patients' do
  content_type :json
  xml = request.body.read
  doc = Nokogiri::XML(xml) do |config|
    config.options = Nokogiri::XML::ParseOptions::NOENT | Nokogiri::XML::ParseOptions::DTDLOAD  # XXE
  end
  patients = doc.xpath('//patient').map { |p| { name: p.at('name')&.text, dob: p.at('dob')&.text } }
  { imported: patients.length, patients: patients }.to_json
end
