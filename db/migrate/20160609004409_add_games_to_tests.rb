class AddGamesToTests < ActiveRecord::Migration
  def change
    add_column :tests, :game_id, :integer
  end
end
