class ApplicationController < ActionController::Base
  include PublicActivity::StoreController
  impersonates :user

  # Prevent CSRF attacks by raising an exception.
  # For APIs, you may want to use :null_session instead.
  protect_from_forgery with: :exception

  before_action :authenticate_user!
  before_filter :update_sanitized_params, if: :devise_controller?

  private

  def update_sanitized_params
    devise_parameter_sanitizer.permit(:sign_up) do |u|
      u.permit(:username, :email, :password, :password_confirmation)
    end
  end
end
