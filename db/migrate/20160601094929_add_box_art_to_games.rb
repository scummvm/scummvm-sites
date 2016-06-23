class AddBoxArtToGames < ActiveRecord::Migration
  def change
    add_column :games, :box_art, :string
  end
end
