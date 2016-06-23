class CreateEngines < ActiveRecord::Migration
  def change
    create_table :engines do |t|
      t.string :name
      t.string :code
      t.integer :introductory_release_id

      t.timestamps null: false
    end
  end
end
