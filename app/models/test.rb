class Test < ActiveRecord::Base
  include PublicActivity::Model
  tracked only: [:create], owner: Proc.new { |controller, model| controller.current_user }

  belongs_to :version
  belongs_to :user
  belongs_to :release
  belongs_to :game

  validates :comment, presence: true
  validates :user_system, presence: true
  validates :tested_at,
    format: {
      with: /\A\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])\z/,
      message: "Date expected in format of YYYY-MM-DD, with MM and DD to be valid"
    }, unless: Proc.new { |c| c.tested_at.blank? }

  default_scope { order(created_at: :desc) }
end
