class Test < ActiveRecord::Base
  include PublicActivity::Model
  tracked only: [:create], owner: Proc.new { |controller, model| controller.current_user }

  belongs_to :version
  belongs_to :user
  belongs_to :release
  belongs_to :game

  validates :comment, presence: true
  validates :user_system, presence: true

  default_scope { order(created_at: :desc) }
end
