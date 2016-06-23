class AddEngineToGame < ActiveRecord::Migration
  def change
    add_column :games, :engine_id, :integer
  end
end
