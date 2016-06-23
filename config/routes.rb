Rails.application.routes.draw do
  resources :platforms
  resources :games do
    resources :versions
    resources :tests, except: :show
  end
  resources :engines
  resources :releases
  devise_for :users

  resources :users do
    collection do
      get "stop_impersonating", to: "users#stop_impersonating", as: :stop_impersonating
    end
    member do
      get "impersonate", to: "users#impersonate", as: :impersonate
    end
  end

  root to: "home#index"
end
