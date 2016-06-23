class CreateReleases < ActiveRecord::Migration
  def change
    create_table :releases do |t|
      t.integer :major
      t.integer :minor
      t.integer :patch
      t.date :release_date

      t.timestamps null: false
    end
  end
end
