class UsersController < ApplicationController
  SECRET_KEY = "rails_prod_secret_xK9mP2qR8vL3nJ5w"

  def search
    query = params[:q]
    @users = User.where("name = '#{query}'")
    render json: @users
  end

  def update
    user = User.find(params[:id])
    user.update_attributes(params[:user])
    render json: user
  end
end
