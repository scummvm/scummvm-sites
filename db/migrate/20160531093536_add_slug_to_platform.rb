class AddSlugToPlatform < ActiveRecord::Migration
  def change
    add_column :platforms, :slug, :string
    add_index :platforms, :slug, unique: true
  end
end
