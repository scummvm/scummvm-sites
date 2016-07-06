class TestsController < ApplicationController
  before_action :set_parents
  before_action :set_test, only: [:show, :edit, :update, :destroy]

  def index
    @tests = Test.all
  end

  def new
    @test = @game.tests.new
  end

  def edit
  end

  def create
    @test = @game.tests.new(test_params)
    @test.user = current_user

    respond_to do |format|
      if @test.save
        format.html { redirect_to [@game], notice: 'Test was successfully created.' }
        format.json { render :show, status: :created, location: @test }
      else
        format.html { render :new }
        format.json { render json: @test.errors, status: :unprocessable_entity }
      end
    end
  end

  def update
    respond_to do |format|
      if @test.update(test_params)
        format.html { redirect_to @test, notice: 'Test was successfully updated.' }
        format.json { render :show, status: :ok, location: @test }
      else
        format.html { render :edit }
        format.json { render json: @test.errors, status: :unprocessable_entity }
      end
    end
  end

  def destroy
    @test.destroy
    respond_to do |format|
      format.html { redirect_to tests_url, notice: 'Test was successfully destroyed.' }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_parents
      @game = Game.friendly.find(params[:game_id])
    end

    def set_test
      @test = Test.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def test_params
      params.require(:test).permit(:game_id, :version_id, :user_id, :compatibility, :comment, :release_id, :release_notes, :user_system, :tested_at)
    end
end
