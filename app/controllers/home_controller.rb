class HomeController < ApplicationController
  def index
    @activities = PublicActivity::Activity.order(created_at: :desc).page(params[:page]).per(25)
  end
end
